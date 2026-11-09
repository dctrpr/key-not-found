import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const canvas = document.querySelector('#scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setClearColor(0x101216, 1);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x101216, 900, 3500);

const camera = new THREE.PerspectiveCamera(45, 1, 1, 10000);
camera.position.set(0, -900, 1350);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.target.set(0, 0, 0);

const root = new THREE.Group();
scene.add(root);

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2(-2, -2);
const hoverText = document.querySelector('#hoverText');
const textureLoader = new THREE.TextureLoader();
const pageScale = 0.22;

const layers = {
  pages: new THREE.Group(),
  rays: new THREE.Group(),
};

Object.values(layers).forEach((layer) => root.add(layer));

const pageGroups = new Map();
const pageInfo = new Map();
let hoverables = [];
const layerObjects = {
  chars: [],
  important: [],
  highlights: [],
  manualHighlights: [],
  reflections: [],
  anchors: [],
};
const charTextures = new Map();
const lineGroups = new Map();
const correctionKey = 'max-keiser-3d-text-corrections-v1';
let corrections = { lines: {} };
let currentLayout = 'spread';
let data;
let transcriptSources = {};
let annotatedTranscript = [];

function pageLocal(page, x, y, z = 0) {
  return new THREE.Vector3(
    (x - page.width / 2) * pageScale,
    (page.height / 2 - y) * pageScale,
    z,
  );
}

function pageWorld(pageNo, point) {
  const page = pageInfo.get(pageNo);
  const group = pageGroups.get(pageNo);
  const local = pageLocal(page, point[0], point[1], point[2] || 0);
  return group.localToWorld(local);
}

function makeTextTexture(char, style = {}) {
  const important = !!style.bold;
  const highlight = style.highlight || 'plain';
  const key = `${char}:${important ? 'bold' : 'plain'}:${highlight}`;
  if (charTextures.has(key)) return charTextures.get(key);
  const size = important ? 96 : 64;
  const canvas2 = document.createElement('canvas');
  canvas2.width = size;
  canvas2.height = size;
  const ctx = canvas2.getContext('2d');
  ctx.clearRect(0, 0, size, size);
  ctx.font = `${important ? 700 : 500} ${important ? 48 : 36}px ui-monospace, SFMono-Regular, Menlo, monospace`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = highlight === 'black' ? '#ffffff' : '#f4f7fa';
  if (important) {
    ctx.fillStyle = highlight === 'orange' ? '#101216' : '#ffb14c';
    ctx.shadowColor = highlight === 'black' ? '#ffffff' : '#ff9b2e';
    ctx.shadowBlur = 12;
  }
  ctx.fillText(char === ' ' ? '·' : char, size / 2, size / 2 + 2);
  const texture = new THREE.CanvasTexture(canvas2);
  texture.colorSpace = THREE.SRGBColorSpace;
  charTextures.set(key, texture);
  return texture;
}

function parseMarkedText(input) {
  const chars = [];
  let bold = false;
  let highlight = null;
  for (let i = 0; i < input.length; i += 1) {
    if (input.startsWith('**', i)) {
      bold = !bold;
      i += 1;
      continue;
    }
    if (input.startsWith('[[', i)) {
      highlight = highlight === 'orange' ? null : 'orange';
      i += 1;
      continue;
    }
    if (input.startsWith(']]', i)) {
      if (highlight === 'orange') highlight = null;
      i += 1;
      continue;
    }
    if (input.startsWith('{{', i)) {
      highlight = highlight === 'black' ? null : 'black';
      i += 1;
      continue;
    }
    if (input.startsWith('~~', i)) {
      highlight = highlight === 'black' ? null : 'black';
      i += 1;
      continue;
    }
    if (input.startsWith('}}', i)) {
      if (highlight === 'black') highlight = null;
      i += 1;
      continue;
    }
    chars.push({ c: input[i], bold, highlight });
  }
  return chars;
}

function stripMarkup(input) {
  return parseMarkedText(input).map((item) => item.c).join('');
}

function loadCorrections() {
  try {
    const stored = JSON.parse(localStorage.getItem(correctionKey) || '{"lines":{}}');
    corrections = stored && stored.lines ? stored : { lines: {} };
  } catch {
    corrections = { lines: {} };
  }
}

function saveCorrections() {
  localStorage.setItem(correctionKey, JSON.stringify(corrections));
}

function lineText(line, useCorrection = true) {
  if (useCorrection && corrections.lines[line.id] !== undefined) return corrections.lines[line.id];
  return line.words.map((word) => word.text).join(' ');
}

function plainLineText(line, useCorrection = true) {
  return stripMarkup(lineText(line, useCorrection));
}

function buildLineGroups() {
  data.pages.forEach((page) => {
    const sorted = [...page.words].sort((a, b) => a.center[1] - b.center[1] || a.center[0] - b.center[0]);
    const lines = [];
    sorted.forEach((word) => {
      const y = word.center[1];
      let line = lines.find((candidate) => Math.abs(candidate.y - y) <= 28);
      if (!line) {
        line = { id: `p${page.page}l${lines.length}`, page: page.page, y, words: [] };
        lines.push(line);
      }
      line.words.push(word);
      line.y = (line.y * (line.words.length - 1) + y) / line.words.length;
    });

    lines.forEach((line, index) => {
      line.id = `p${page.page}l${index}`;
      line.words.sort((a, b) => a.center[0] - b.center[0]);
      const boxes = line.words.map((word) => word.box);
      line.box = [
        Math.min(...boxes.map((box) => box[0])),
        Math.min(...boxes.map((box) => box[1])),
        Math.max(...boxes.map((box) => box[2])),
        Math.max(...boxes.map((box) => box[3])),
      ];
    });
    lineGroups.set(page.page, lines);
  });
}

function removeCharObjectsForPage(pageNo) {
  layerObjects.chars = layerObjects.chars.filter((object) => {
    if (object.userData.page !== pageNo) return true;
    hoverables = hoverables.filter((item) => item !== object);
    object.parent?.remove(object);
    object.material?.dispose?.();
    return false;
  });
  layerObjects.manualHighlights = layerObjects.manualHighlights.filter((object) => {
    if (object.userData.page !== pageNo) return true;
    hoverables = hoverables.filter((item) => item !== object);
    object.parent?.remove(object);
    object.geometry?.dispose?.();
    object.material?.dispose?.();
    return false;
  });
}

function addCharSprite(page, group, char, x, y, style = {}) {
  if (!char.trim()) return;
  const corrected = !!style.corrected;
  const texture = makeTextTexture(char, style);
  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    opacity: corrected || style.bold || style.highlight ? 0.96 : 0.76,
    depthWrite: false,
  });
  const sprite = new THREE.Sprite(material);
  sprite.position.copy(pageLocal(page, x, y, style.highlight ? 27 : corrected ? 22 : 14));
  const size = style.bold ? 12 : corrected || style.highlight ? 9 : 8;
  sprite.scale.set(size, size, 1);
  sprite.userData = { layer: corrected ? 'corrected-char' : 'char', page: page.page, text: char };
  group.add(sprite);
  layerObjects.chars.push(sprite);
}

function addManualHighlightPlane(page, group, box, kind) {
  const [x1, y1, x2, y2] = box;
  const rect = new THREE.Mesh(
    new THREE.PlaneGeometry(Math.max(1, (x2 - x1) * pageScale), Math.max(1, (y2 - y1) * pageScale)),
    new THREE.MeshBasicMaterial({
      color: kind === 'black' ? 0x05070a : 0xff9b2e,
      transparent: true,
      opacity: kind === 'black' ? 0.76 : 0.56,
      side: THREE.DoubleSide,
    }),
  );
  rect.position.copy(pageLocal(page, (x1 + x2) / 2, (y1 + y2) / 2, kind === 'black' ? 24 : 18));
  rect.userData = { layer: `${kind}-manual-highlight`, page: page.page, text: kind };
  group.add(rect);
  layerObjects.manualHighlights.push(rect);
  hoverables.push(rect);
}

function addTextAcrossBox(page, group, text, box, corrected) {
  const [x1, y1, x2, y2] = box;
  const width = Math.max(1, x2 - x1);
  const y = (y1 + y2) / 2;
  const chars = parseMarkedText(text);
  const count = Math.max(1, chars.length);
  let activeHighlight = null;
  let activeStart = 0;
  const closeHighlight = (endIndex) => {
    if (!activeHighlight || endIndex <= activeStart) return;
    const hx1 = x1 + (activeStart / count) * width;
    const hx2 = x1 + (endIndex / count) * width;
    addManualHighlightPlane(page, group, [hx1, y1, hx2, y2], activeHighlight);
  };
  chars.forEach((item, index) => {
    if (item.highlight !== activeHighlight) {
      closeHighlight(index);
      activeHighlight = item.highlight;
      activeStart = index;
    }
    const x = x1 + ((index + 0.5) / count) * width;
    addCharSprite(page, group, item.c, x, y, { corrected, bold: item.bold, highlight: item.highlight });
  });
  closeHighlight(chars.length);
}

function rebuildPageCharacters(pageNo) {
  const page = pageInfo.get(pageNo);
  const group = pageGroups.get(pageNo);
  const lines = lineGroups.get(pageNo) || [];
  if (!page || !group) return;
  removeCharObjectsForPage(pageNo);

  lines.forEach((line) => {
    const corrected = corrections.lines[line.id] !== undefined;
    if (corrected) {
      addTextAcrossBox(page, group, corrections.lines[line.id], line.box, true);
      return;
    }
    line.words.forEach((word) => {
      addTextAcrossBox(page, group, word.text, word.box, false);
    });
  });
}

function rebuildAllCharacters() {
  data.pages.forEach((page) => rebuildPageCharacters(page.page));
  setLayerVisibility();
  updateCorrectionStats();
}

function addPage(page) {
  pageInfo.set(page.page, page);
  const group = new THREE.Group();
  group.userData.page = page.page;
  pageGroups.set(page.page, group);
  root.add(group);

  const width = page.width * pageScale;
  const height = page.height * pageScale;
  const texture = textureLoader.load(page.image);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
  const material = new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide });
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(width, height), material);
  plane.userData = { layer: 'page', page: page.page };
  group.add(plane);
  layers.pages.add(group);

  const edge = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.PlaneGeometry(width, height)),
    new THREE.LineBasicMaterial({ color: 0x617084, transparent: true, opacity: 0.65 }),
  );
  group.add(edge);

  page.words.forEach((word) => {
    if (word.importance <= 0) return;
    const [x1, y1, x2, y2] = word.box;
    const pos = pageLocal(page, (x1 + x2) / 2, (y1 + y2) / 2, 9 + Math.min(20, word.importance * 3));
    const w = Math.max(4, (x2 - x1) * pageScale);
    const h = Math.max(4, (y2 - y1) * pageScale);
    const hot = new THREE.Mesh(
      new THREE.PlaneGeometry(w, h),
      new THREE.MeshBasicMaterial({
        color: word.importance >= 7 ? 0xff5ebc : 0x55d6ff,
        transparent: true,
        opacity: word.importance >= 7 ? 0.42 : 0.28,
        side: THREE.DoubleSide,
      }),
    );
    hot.position.copy(pos);
    hot.userData = { layer: 'important', page: page.page, text: word.text, reasons: word.reasons };
    group.add(hot);
    layerObjects.important.push(hot);
    hoverables.push(hot);
  });

  page.highlights.forEach((highlight) => {
    const [x1, y1, x2, y2] = highlight.box;
    const rect = new THREE.Mesh(
      new THREE.PlaneGeometry((x2 - x1) * pageScale, (y2 - y1) * pageScale),
      new THREE.MeshBasicMaterial({ color: 0xff9b2e, transparent: true, opacity: 0.48, side: THREE.DoubleSide }),
    );
    rect.position.copy(pageLocal(page, (x1 + x2) / 2, (y1 + y2) / 2, 5));
    rect.userData = { layer: 'highlight', page: page.page, text: highlight.id };
    group.add(rect);
    layerObjects.highlights.push(rect);
    hoverables.push(rect);
  });
}

function addReflections() {
  data.reflections.forEach((reflection) => {
    const page = pageInfo.get(reflection.target);
    const group = pageGroups.get(reflection.target);
    const [x1, y1, x2, y2] = reflection.targetBox;
    const rect = new THREE.Mesh(
      new THREE.PlaneGeometry(Math.max(1, (x2 - x1) * pageScale), Math.max(1, (y2 - y1) * pageScale)),
      new THREE.MeshBasicMaterial({ color: 0x8ee56f, transparent: true, opacity: 0.30, side: THREE.DoubleSide }),
    );
    rect.position.copy(pageLocal(page, (x1 + x2) / 2, (y1 + y2) / 2, 22));
    rect.userData = {
      layer: 'reflection',
      page: reflection.target,
      text: `${reflection.source} → ${reflection.target}: ${reflection.text || reflection.chars || 'blank'}`,
    };
    group.add(rect);
    layerObjects.reflections.push(rect);
    hoverables.push(rect);
  });
}

function addAnchors() {
  data.anchors.forEach((anchor) => {
    const page = pageInfo.get(anchor.page);
    const group = pageGroups.get(anchor.page);
    if (!page || !group) return;
    const sphere = new THREE.Mesh(
      new THREE.SphereGeometry(12, 18, 18),
      new THREE.MeshBasicMaterial({ color: anchor.id.includes('pill') ? 0xff9b2e : 0xff5ebc }),
    );
    sphere.position.copy(pageLocal(page, anchor.point[0], anchor.point[1], 42));
    sphere.userData = { layer: 'anchor', page: anchor.page, text: anchor.id };
    group.add(sphere);
    layerObjects.anchors.push(sphere);
    hoverables.push(sphere);
  });
}

function addRays() {
  const anchorById = new Map(data.anchors.map((anchor) => [anchor.id, anchor]));
  data.raySelections.slice(0, 28).forEach((selection, idx) => {
    const a = anchorById.get(selection.a);
    const b = anchorById.get(selection.b);
    if (!a || !b) return;
    const start = pageWorld(76, [a.point[0], a.point[1], 62]);
    const end = pageWorld(76, [b.point[0], b.point[1], 62]);
    const geometry = new THREE.BufferGeometry().setFromPoints([start, end]);
    const color = idx < 4 ? 0xff5ebc : idx < 10 ? 0xff9b2e : 0x55d6ff;
    const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({ color, transparent: true, opacity: idx < 10 ? 0.82 : 0.42 }));
    line.userData = { layer: 'ray', page: 76, text: `${selection.rank}. ${selection.text}` };
    layers.rays.add(line);
    hoverables.push(line);
  });
}

function setLayout(mode) {
  currentLayout = mode;
  const positions = {
    spread: {
      75: [-560, 330, 0, 0],
      76: [0, 330, 0, 0],
      77: [560, 330, 0, 0],
      78: [-560, -380, 0, 0],
      79: [0, -380, 0, 0],
      80: [560, -380, 0, 0],
    },
    stack: {
      75: [-180, 0, -250, -0.20],
      76: [-110, 0, -130, -0.12],
      77: [-40, 0, -10, -0.04],
      78: [40, 0, 110, 0.04],
      79: [110, 0, 230, 0.12],
      80: [180, 0, 350, 0.20],
    },
    fold: {
      75: [-280, 320, -130, 0.42],
      79: [280, 320, -130, -0.42],
      76: [-280, -380, 130, 0.42],
      78: [280, -380, 130, -0.42],
      77: [0, -20, 330, 0],
      80: [610, -20, 420, -0.2],
    },
  }[mode];

  pageGroups.forEach((group, pageNo) => {
    const p = positions[pageNo];
    group.position.set(p[0], p[1], p[2]);
    group.rotation.y = p[3];
  });

  layers.rays.clear();
  addRays();
}

function setLayerVisibility() {
  layers.pages.visible = document.querySelector('#togglePages').checked;
  layerObjects.chars.forEach((object) => { object.visible = document.querySelector('#toggleChars').checked; });
  layerObjects.important.forEach((object) => { object.visible = document.querySelector('#toggleImportant').checked; });
  layerObjects.highlights.forEach((object) => { object.visible = document.querySelector('#toggleHighlights').checked; });
  layerObjects.manualHighlights.forEach((object) => { object.visible = document.querySelector('#toggleHighlights').checked; });
  layerObjects.reflections.forEach((object) => { object.visible = document.querySelector('#toggleReflections').checked; });
  layerObjects.anchors.forEach((object) => { object.visible = document.querySelector('#toggleAnchors').checked; });
  layers.rays.visible = document.querySelector('#toggleRays').checked;
}

function focusPage(value) {
  pageGroups.forEach((group, pageNo) => {
    group.visible = value === 'all' || Number(value) === pageNo;
  });
}

function renderFindings() {
  const list = document.querySelector('#findings');
  const page76 = data.pages.find((page) => page.page === 76);
  const top = data.raySelections[0];
  const findings = [
    `Page 76 has the densest clue concentration: ${page76.words.filter((word) => word.importance > 0).length} important words after ray and focus scoring.`,
    `The strongest ray pull is “${top.text}”, which lands on President/Nayib/volcano language but did not produce an active key in direct checks.`,
    `The mirror boxes preserve the earlier result: reflected highlights select readable phrases, but their direct key and index derivations are clean.`,
    `The 3D fold view shows the 76/79 visual system as orientation evidence first; it still needs a stricter selector before more chain checks are worthwhile.`,
    `The 3D word labels are not exact text for the active lower page-76 targets; use the Text Authority panel or corrected transcript before extracting wording.`,
    `Manual bold markup is not source-faithful for the active lower corridor; use the typography authority sheet for DOCM Typeka/bold/highlight states.`,
    `The page-76 typography overlay keeps the four live anchors together: black $1 billion/Volcano Bonds, orange buying the dip/shitcoiner at heart, and Typeka Mix nearby context.`,
  ];
  list.innerHTML = findings.map((item) => `<li>${item}</li>`).join('');
}

function correctionCount() {
  return Object.keys(corrections.lines).length;
}

function displayCharCount() {
  let total = 0;
  data.pages.forEach((page) => {
    const lines = lineGroups.get(page.page) || [];
    lines.forEach((line) => {
      total += [...plainLineText(line)].filter((char) => char.trim()).length;
    });
  });
  return total;
}

function updateCorrectionStats() {
  document.querySelector('#charCount').textContent = displayCharCount().toLocaleString();
  const status = document.querySelector('#correctionStatus');
  if (status) {
    status.textContent = `${correctionCount()} corrected line${correctionCount() === 1 ? '' : 's'} saved in this browser.`;
  }
}

function populateCorrectionLines() {
  const pageNo = Number(document.querySelector('#correctionPage').value);
  const select = document.querySelector('#correctionLine');
  const lines = lineGroups.get(pageNo) || [];
  select.innerHTML = '';
  lines.forEach((line, index) => {
    const option = document.createElement('option');
    const corrected = corrections.lines[line.id] !== undefined ? ' *' : '';
    option.value = line.id;
    option.textContent = `${String(index + 1).padStart(2, '0')}${corrected} ${plainLineText(line, false).slice(0, 76)}`;
    select.appendChild(option);
  });
  updateCorrectionEditor();
}

function selectedCorrectionLine() {
  const pageNo = Number(document.querySelector('#correctionPage').value);
  const lineId = document.querySelector('#correctionLine').value;
  return (lineGroups.get(pageNo) || []).find((line) => line.id === lineId);
}

function updateCorrectionEditor() {
  const line = selectedCorrectionLine();
  const preview = document.querySelector('#ocrLinePreview');
  const textarea = document.querySelector('#correctionText');
  if (!line) {
    preview.textContent = '';
    textarea.value = '';
    return;
  }
  preview.textContent = plainLineText(line, false);
  textarea.value = lineText(line, true);
}

function applyCorrection() {
  const line = selectedCorrectionLine();
  if (!line) return;
  const value = document.querySelector('#correctionText').value;
  if (value === plainLineText(line, false)) {
    delete corrections.lines[line.id];
  } else {
    corrections.lines[line.id] = value;
  }
  saveCorrections();
  rebuildPageCharacters(line.page);
  populateCorrectionLines();
  document.querySelector('#correctionLine').value = line.id;
  updateCorrectionEditor();
  updateCorrectionStats();
}

function resetCorrection() {
  const line = selectedCorrectionLine();
  if (!line) return;
  delete corrections.lines[line.id];
  saveCorrections();
  rebuildPageCharacters(line.page);
  populateCorrectionLines();
  document.querySelector('#correctionLine').value = line.id;
  updateCorrectionEditor();
  updateCorrectionStats();
}

function clearCorrections() {
  corrections = { lines: {} };
  saveCorrections();
  rebuildAllCharacters();
  populateCorrectionLines();
}

function exportCorrections() {
  const correctedLines = [];
  data.pages.forEach((page) => {
    (lineGroups.get(page.page) || []).forEach((line) => {
      if (corrections.lines[line.id] === undefined) return;
      correctedLines.push({
        id: line.id,
        page: line.page,
        box: line.box,
        ocr: plainLineText(line, false),
        corrected: corrections.lines[line.id],
        correctedPlain: stripMarkup(corrections.lines[line.id]),
      });
    });
  });
  const payload = {
    exportedAt: new Date().toISOString(),
    source: 'Max Keiser Puzzle 3D Article Map',
    correctedLines,
    corrections,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'max-keiser-3d-text-corrections.json';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function wrapTextareaSelection(before, after) {
  const textarea = document.querySelector('#correctionText');
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selected = textarea.value.slice(start, end);
  textarea.value = `${textarea.value.slice(0, start)}${before}${selected}${after}${textarea.value.slice(end)}`;
  const cursorStart = start + before.length;
  const cursorEnd = cursorStart + selected.length;
  textarea.focus();
  textarea.setSelectionRange(cursorStart, cursorEnd);
}

function stripTextareaMarkup() {
  const textarea = document.querySelector('#correctionText');
  textarea.value = stripMarkup(textarea.value);
  textarea.focus();
}

function setupCorrectionUi() {
  document.querySelector('#correctionPage').addEventListener('change', populateCorrectionLines);
  document.querySelector('#correctionLine').addEventListener('change', updateCorrectionEditor);
  document.querySelector('#applyCorrection').addEventListener('click', applyCorrection);
  document.querySelector('#resetCorrection').addEventListener('click', resetCorrection);
  document.querySelector('#clearCorrections').addEventListener('click', clearCorrections);
  document.querySelector('#exportCorrections').addEventListener('click', exportCorrections);
  document.querySelector('#markBold').addEventListener('click', () => wrapTextareaSelection('**', '**'));
  document.querySelector('#markOrange').addEventListener('click', () => wrapTextareaSelection('[[', ']]'));
  document.querySelector('#markBlack').addEventListener('click', () => wrapTextareaSelection('{{', '}}'));
  document.querySelector('#stripMarkup').addEventListener('click', stripTextareaMarkup);
  populateCorrectionLines();
}

function splitAnnotatedTranscript(raw) {
  const markers = [
    { id: 'page1', label: 'Page 1', pattern: /^BITCOIN IS TOXIC AF/m },
    { id: 'page2', label: 'Second page', pattern: /^Second page$/m },
    { id: 'page3', label: 'Page 3', pattern: /^page 3$/mi },
    { id: 'page4', label: 'Page 4', pattern: /^Page 4$/m },
    { id: 'page5', label: 'Page 5', pattern: /^Page 5\s*$/m },
  ];
  const starts = markers
    .map((marker) => {
      const match = raw.match(marker.pattern);
      return match ? { ...marker, index: match.index } : null;
    })
    .filter(Boolean)
    .sort((a, b) => a.index - b.index);
  return starts.map((marker, idx) => {
    const next = starts[idx + 1]?.index ?? raw.length;
    return {
      id: marker.id,
      label: marker.label,
      text: raw.slice(marker.index, next).trim(),
    };
  });
}

function splitMarkdownTranscript(raw) {
  const parts = [
    { id: 'md_1', label: 'Markdown 1', text: '' },
    { id: 'md_2', label: 'Markdown 2', text: '' },
    { id: 'md_3', label: 'Markdown 3', text: '' },
    { id: 'md_4', label: 'Markdown 4', text: '' },
    { id: 'md_5', label: 'Markdown 5', text: '' },
  ];
  const paragraphs = raw.split(/\n\s*\n/);
  let partIndex = 0;
  paragraphs.forEach((paragraph) => {
    const text = paragraph.trim();
    if (!text) return;
    if (text.includes('**Get some toxicity. Get some bitcoin. Open your heart to**')) partIndex = 1;
    if (text.includes('Meanwhile, back in El Salvador')) partIndex = 2;
    if (text.includes("**We've never had an economy and a money**")) partIndex = 3;
    if (text.includes('To wrap this up, as we move from a war and violence economy')) partIndex = 4;
    parts[partIndex].text += `${parts[partIndex].text ? '\n\n' : ''}${paragraph.trim()}`;
  });
  return parts.filter((part) => part.text);
}

function updateTranscriptViewer() {
  const id = document.querySelector('#transcriptPage').value;
  const item = annotatedTranscript.find((entry) => entry.id === id);
  document.querySelector('#transcriptText').value = item?.text || '';
}

function copyTranscriptToCorrection() {
  const text = document.querySelector('#transcriptText').value;
  document.querySelector('#correctionText').value = text;
  document.querySelector('#correctionText').focus();
}

function downloadAnnotatedTranscript() {
  const text = annotatedTranscript.map((entry) => entry.text).join('\n\n');
  const blob = new Blob([text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'max-keiser-user-annotated-transcript.txt';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function populateTranscriptParts() {
  const source = document.querySelector('#transcriptSource').value;
  annotatedTranscript = transcriptSources[source] || [];
  const select = document.querySelector('#transcriptPage');
  select.innerHTML = '';
  annotatedTranscript.forEach((entry) => {
    const option = document.createElement('option');
    option.value = entry.id;
    option.textContent = entry.label;
    select.appendChild(option);
  });
  updateTranscriptViewer();
}

async function setupTranscriptUi() {
  const [notesRaw, markdownRaw] = await Promise.all([
    fetch('./user_annotated_transcript.txt').then((response) => response.text()),
    fetch('./user_markdown_transcript.md').then((response) => response.text()),
  ]);
  transcriptSources = {
    notes: splitAnnotatedTranscript(notesRaw),
    markdown: splitMarkdownTranscript(markdownRaw),
  };
  document.querySelector('#transcriptSource').addEventListener('change', populateTranscriptParts);
  document.querySelector('#transcriptPage').addEventListener('change', updateTranscriptViewer);
  document.querySelector('#copyTranscript').addEventListener('click', copyTranscriptToCorrection);
  document.querySelector('#downloadTranscript').addEventListener('click', downloadAnnotatedTranscript);
  populateTranscriptParts();
}

function resize() {
  const rect = canvas.parentElement.getBoundingClientRect();
  renderer.setSize(rect.width, rect.height, false);
  camera.aspect = rect.width / Math.max(1, rect.height);
  camera.updateProjectionMatrix();
}

function animate() {
  controls.update();
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(hoverables, false);
  if (hits.length) {
    const userData = hits[0].object.userData;
    hoverText.textContent = `${userData.layer} p${userData.page}: ${userData.text}`;
  }
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

async function init() {
  const params = new URLSearchParams(window.location.search);
  const requestedLayout = params.get('layout') || 'spread';
  const requestedFocus = params.get('focus') || 'all';
  data = await fetch('./article_3d_map_data.json').then((response) => response.json());
  loadCorrections();
  buildLineGroups();
  data.pages.forEach(addPage);
  rebuildAllCharacters();
  setLayout(['spread', 'fold', 'stack'].includes(requestedLayout) ? requestedLayout : 'spread');
  addReflections();
  addAnchors();
  layers.rays.clear();
  addRays();
  renderFindings();
  setLayerVisibility();

  document.querySelector('#wordCount').textContent = data.pages.reduce((sum, page) => sum + page.words.length, 0).toLocaleString();
  document.querySelector('#anchorCount').textContent = data.anchors.length.toLocaleString();
  document.querySelector('#reflectionCount').textContent = data.reflections.length.toLocaleString();
  updateCorrectionStats();
  setupCorrectionUi();
  await setupTranscriptUi();

  document.querySelectorAll('[data-layout]').forEach((button) => {
    button.classList.toggle('active', button.dataset.layout === currentLayout);
    button.addEventListener('click', () => {
      document.querySelectorAll('[data-layout]').forEach((item) => item.classList.remove('active'));
      button.classList.add('active');
      setLayout(button.dataset.layout);
    });
  });

  document.querySelectorAll('input[type="checkbox"]').forEach((input) => input.addEventListener('change', setLayerVisibility));
  document.querySelector('#focusSelect').addEventListener('change', (event) => focusPage(event.target.value));
  document.querySelector('#focusSelect').value = requestedFocus;
  focusPage(requestedFocus);
  window.addEventListener('resize', resize);
  window.addEventListener('pointermove', (event) => {
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  });

  resize();
  animate();
}

init().catch((error) => {
  hoverText.textContent = error.message;
  throw error;
});
