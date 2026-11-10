import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { visualPageUrl, visualPairPages, visualSource } from "./VisualLab";
import type { VisualLabView, VisualZoomRequest } from "./VisualLab";

type SceneProps = {
  view: VisualLabView;
  resetToken: number;
  zoomRequest: VisualZoomRequest;
  descriptionId: string;
  onProgress: (loaded: number, total: number) => void;
  onReady: () => void;
  onFailure: () => void;
  onExit: () => void;
};
type SceneAPI = { setView: (view: VisualLabView) => void; zoom: (amount: number) => void };
type Card = { group: THREE.Group; face: THREE.MeshBasicMaterial; edge: THREE.MeshBasicMaterial };
const WIDTH = 2.4;

/** Static source cards, rendered only on interaction, resize or texture arrival. */
export default function VisualScene({ view, resetToken, zoomRequest, descriptionId, onProgress, onReady, onFailure, onExit }: SceneProps) {
  const host = useRef<HTMLDivElement>(null);
  const api = useRef<SceneAPI | null>(null);
  const initialView = useRef(view);

  useEffect(() => {
    const element = host.current;
    if (!element) return;
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: "low-power" });
    } catch { onFailure(); return; }

    let disposed = false;
    let failed = false;
    let frame = 0;
    let visible = true;
    let current = initialView.current;
    const source = visualSource(current.source);
    const pages: readonly number[] = source.pages;
    const height = WIDTH * source.height / source.width;
    const pageKey = (page: number) => visualPageUrl(page, initialView.current.source);
    let loadGeneration = 0;
    const abort = new AbortController();
    const textures = new Map<string, THREE.Texture>();
    const pending = new Map<string, Promise<void>>();
    let activeLoads = 0;
    const loadWaiters: Array<() => void> = [];
    const cleanups: Array<() => void> = [];
    const geometries: THREE.BufferGeometry[] = [];
    const materials: THREE.Material[] = [];
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0c0d0a);
    const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 70);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    renderer.domElement.tabIndex = 0;
    renderer.domElement.setAttribute("role", "img");
    renderer.domElement.setAttribute("aria-describedby", descriptionId);
    element.appendChild(renderer.domElement);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = false;
    controls.enablePan = true;
    controls.screenSpacePanning = true;
    controls.minDistance = 2.5;
    controls.maxDistance = 25;
    controls.minPolarAngle = 0.2;
    controls.maxPolarAngle = Math.PI - 0.2;

    const fail = () => {
      if (disposed || failed) return;
      failed = true;
      onFailure();
    };
    const render = () => {
      frame = 0;
      if (disposed || failed || !visible || document.hidden) return;
      try { renderer.render(scene, camera); } catch { fail(); }
    };
    const requestRender = () => {
      if (!disposed && !failed && visible && !document.hidden && !frame) frame = requestAnimationFrame(render);
    };
    controls.addEventListener("change", requestRender);

    const board = new THREE.Group();
    scene.add(board);
    const plane = new THREE.PlaneGeometry(WIDTH, height);
    const reflectedPlane = plane.clone();
    const uv = reflectedPlane.getAttribute("uv");
    for (let i = 0; i < uv.count; i++) uv.setX(i, 1 - uv.getX(i));
    uv.needsUpdate = true;
    const edgeGeometry = new THREE.BoxGeometry(WIDTH + .045, height + .045, .034);
    geometries.push(plane, reflectedPlane, edgeGeometry);
    const makeCard = (mirrored = false): Card => {
      const group = new THREE.Group();
      const edge = new THREE.MeshBasicMaterial({ color: 0xf4f1e8 });
      const face = new THREE.MeshBasicMaterial({ color: 0x363a2a });
      materials.push(edge, face);
      group.add(new THREE.Mesh(edgeGeometry, edge));
      const scan = new THREE.Mesh(mirrored ? reflectedPlane : plane, face);
      scan.position.z = .019;
      group.add(scan);
      board.add(group);
      return { group, face, edge };
    };
    const cards = new Map(pages.map((page) => [page, makeCard()]));
    const reflection = makeCard(true);
    const grid = new THREE.GridHelper(35, 70, 0x343c24, 0x20251a);
    grid.rotation.x = Math.PI / 2;
    grid.position.z = -3.2;
    const gridMaterials = Array.isArray(grid.material) ? grid.material : [grid.material];
    gridMaterials.forEach((material) => { material.transparent = true; material.opacity = .4; });
    geometries.push(grid.geometry);
    materials.push(...gridMaterials);
    scene.add(grid);

    const fitCamera = () => {
      const aspect = Math.max(.35, element.clientWidth / Math.max(1, element.clientHeight));
      const worldWidth = current.layout === "stack" ? 6.2 : 5.35;
      const worldHeight = current.layout === "stack" ? 4.1 : 3.55;
      const tangent = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
      const distance = Math.max(5.8, worldWidth / (2 * tangent * aspect), worldHeight / (2 * tangent)) * 1.08;
      camera.position.set(.05, current.layout === "stack" ? .7 : .15, distance);
      controls.target.set(0, 0, current.layout === "stack" ? -.3 : 0);
      controls.update();
      requestRender();
    };
    const resize = () => {
      if (disposed) return;
      const width = Math.max(1, element.clientWidth);
      const height = Math.max(1, element.clientHeight);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      fitCamera();
    };

    // Draw into a bounded viewing texture; the full source image remains a link
    // in the accessible HTML. Only needed pages are fetched, with two loaders.
    const maximumEdge = window.matchMedia("(max-width: 720px)").matches ? 900 : 1400;
    const loadTexture = async (page: number) => {
      const url = pageKey(page);
      if (textures.has(url)) return;
      if (pending.has(url)) return pending.get(url);
      const promise = (async () => {
        await new Promise<void>((resolve) => {
          const enter = () => { activeLoads++; resolve(); };
          if (activeLoads < 2) enter();
          else loadWaiters.push(enter);
        });
        try {
        if (disposed) return;
        const response = await fetch(url, { signal: abort.signal });
        if (!response.ok) throw new Error("Source scan unavailable");
        const blob = await response.blob();
        const width = Math.round(maximumEdge * source.width / source.height);
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = maximumEdge;
        const context = canvas.getContext("2d", { alpha: false });
        if (!context) throw new Error("Viewing texture unavailable");
        let decoded = false;
        if (typeof createImageBitmap === "function") {
          try {
            const bitmap = await createImageBitmap(blob, { resizeWidth: width, resizeHeight: maximumEdge, resizeQuality: "high" });
            if (disposed) { bitmap.close(); return; }
            context.drawImage(bitmap, 0, 0, width, maximumEdge);
            bitmap.close();
            decoded = true;
          } catch { if (disposed) return; }
        }
        if (!decoded) {
          const image = new Image();
          image.decoding = "async";
          image.src = url;
          await image.decode();
          if (disposed) return;
          context.drawImage(image, 0, 0, width, maximumEdge);
          image.src = "";
        }
        if (disposed) return;
        const texture = new THREE.CanvasTexture(canvas);
        texture.colorSpace = THREE.SRGBColorSpace;
        texture.anisotropy = Math.min(4, renderer.capabilities.getMaxAnisotropy());
        textures.set(url, texture);
        const card = cards.get(page)!;
        card.face.map = texture;
        card.face.color.set(0xffffff);
        card.face.needsUpdate = true;
        if (current.page === page) {
          reflection.face.map = texture;
          reflection.face.color.set(0xffffff);
          reflection.face.needsUpdate = true;
        }
        requestRender();
        } finally {
          activeLoads--;
          loadWaiters.shift()?.();
        }
      })();
      pending.set(url, promise);
      return promise;
    };
    const neededPages = (next: VisualLabView) => {
      if (next.layout === "stack") return pages;
      if (next.layout === "mirror") return [next.page];
      return visualPairPages(next);
    };
    const ensurePages = async (next: VisualLabView) => {
      const generation = ++loadGeneration;
      const needed = neededPages(next);
      const update = () => {
        if (disposed || generation !== loadGeneration) return;
        const loaded = needed.filter((page) => textures.has(pageKey(page))).length;
        onProgress(loaded, needed.length);
        if (loaded === needed.length) onReady();
      };
      update();
      const queue = needed.filter((page) => !textures.has(pageKey(page)));
      const worker = async () => {
        while (queue.length && !disposed) {
          const page = queue.shift()!;
          await loadTexture(page);
          update();
        }
      };
      try { await Promise.all([worker(), worker()]); }
      catch { if (!disposed && !abort.signal.aborted && generation === loadGeneration) fail(); }
    };
    const setView = (next: VisualLabView) => {
      if (disposed) return;
      current = next;
      cards.forEach((card, page) => {
        card.group.visible = false;
        card.group.position.set(0, 0, 0);
        card.group.rotation.set(0, 0, 0);
        card.group.scale.setScalar(1);
        card.edge.color.set(page === next.page ? 0xd6ff3c : 0xf4f1e8);
      });
      reflection.group.visible = false;
      if (next.layout === "spread") {
        visualPairPages(next).forEach((page, i) => {
          const card = cards.get(page)!;
          card.group.visible = true;
          card.group.position.x = (i ? 1 : -1) * 1.25;
          card.group.rotation.y = i ? -.045 : .045;
        });
      } else if (next.layout === "stack") {
        pages.forEach((page, i) => {
          const card = cards.get(page)!;
          card.group.visible = true;
          card.group.position.set(-1.75 + i * .48, .22 + i * .09, -1.7 + i * .24);
          card.group.rotation.set(-.04, -.24, -.07);
          card.group.scale.setScalar(.86);
          if (page === next.page) {
            card.group.position.set(1.35, -.15, 1.1);
            card.group.rotation.set(0, -.06, .025);
            card.group.scale.setScalar(1);
          }
        });
      } else {
        const card = cards.get(next.page)!;
        card.group.visible = true;
        card.group.position.x = -1.25;
        card.group.rotation.y = .045;
        reflection.group.visible = true;
        reflection.group.position.set(1.25, 0, 0);
        reflection.group.rotation.set(0, -.045, 0);
        reflection.edge.color.set(0x8c9870);
        reflection.face.map = textures.get(pageKey(next.page)) || null;
        reflection.face.color.set(reflection.face.map ? 0xffffff : 0x363a2a);
        reflection.face.needsUpdate = true;
      }
      renderer.domElement.setAttribute("aria-label", `Interactive ${source.name} source scan view. ${next.layout === "mirror" ? "Page " + next.page + " and its reflected copy, an investigator hypothesis." : next.layout === "stack" ? pages.length + " page cards; page " + next.page + " selected." : "Page " + next.page + " selected in a two-page board."}`);
      fitCamera();
      void ensurePages(next);
    };
    const zoom = (amount: number) => {
      const offset = camera.position.clone().sub(controls.target);
      const distance = THREE.MathUtils.clamp(offset.length() * (amount > 0 ? .82 : 1.22), controls.minDistance, controls.maxDistance);
      camera.position.copy(controls.target).add(offset.setLength(distance));
      controls.update();
      requestRender();
    };
    const keyboard = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); onExit(); return; }
      if (["+", "=", "-"].includes(event.key)) { event.preventDefault(); zoom(event.key === "-" ? -1 : 1); return; }
      if (["0", "Home"].includes(event.key)) { event.preventDefault(); fitCamera(); return; }
      if (!event.key.startsWith("Arrow")) return;
      event.preventDefault();
      const spherical = new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
      if (event.key === "ArrowLeft") spherical.theta += .12;
      if (event.key === "ArrowRight") spherical.theta -= .12;
      if (event.key === "ArrowUp") spherical.phi -= .12;
      if (event.key === "ArrowDown") spherical.phi += .12;
      spherical.phi = THREE.MathUtils.clamp(spherical.phi, .2, Math.PI - .2);
      camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));
      controls.update();
      requestRender();
    };
    const lost = (event: Event) => { event.preventDefault(); fail(); };
    renderer.domElement.addEventListener("keydown", keyboard);
    renderer.domElement.addEventListener("webglcontextlost", lost);
    document.addEventListener("visibilitychange", requestRender);
    const resizeObserver = typeof ResizeObserver === "function" ? new ResizeObserver(resize) : null;
    resizeObserver?.observe(element);
    if (!resizeObserver) window.addEventListener("resize", resize);
    const intersectionObserver = typeof IntersectionObserver === "function" ? new IntersectionObserver((entries) => {
      visible = entries.some((entry) => entry.isIntersecting);
      if (visible) requestRender();
    }) : null;
    intersectionObserver?.observe(element);
    api.current = { setView, zoom };
    resize();
    setView(current);

    cleanups.push(() => resizeObserver?.disconnect(), () => intersectionObserver?.disconnect(), () => window.removeEventListener("resize", resize));
    return () => {
      disposed = true;
      abort.abort();
      api.current = null;
      if (frame) cancelAnimationFrame(frame);
      cleanups.forEach((cleanup) => cleanup());
      renderer.domElement.removeEventListener("keydown", keyboard);
      renderer.domElement.removeEventListener("webglcontextlost", lost);
      document.removeEventListener("visibilitychange", requestRender);
      controls.removeEventListener("change", requestRender);
      controls.dispose();
      geometries.forEach((geometry) => geometry.dispose());
      materials.forEach((material) => material.dispose());
      textures.forEach((texture) => texture.dispose());
      renderer.dispose();
      renderer.forceContextLoss();
      renderer.domElement.remove();
    };
  }, [descriptionId, onProgress, onReady, onFailure, onExit]);

  useEffect(() => { api.current?.setView(view); }, [view.layout, view.page, view.source, resetToken]);
  useEffect(() => { if (zoomRequest.serial) api.current?.zoom(zoomRequest.amount); }, [zoomRequest.serial, zoomRequest.amount]);
  return <div className="visual-scene" ref={host} />;
}
