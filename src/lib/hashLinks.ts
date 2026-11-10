/**
 * In-page links that also drive view state (#method-<id>, #open-leads,
 * #update-<id>).
 *
 * A hashchange covers a new hash, the browser's back and forward buttons and a
 * typed or shared URL. It does not fire when a link repeats the hash already in
 * the address bar, so those clicks are followed directly. Nothing is cancelled:
 * ordinary anchors, history and the browser's own scrolling keep working.
 */
export function followHashLinks(follow: (hash: string) => void) {
  const fromLocation = () => follow(window.location.hash);
  const fromClick = (event: MouseEvent) => {
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    )
      return;
    const link =
      event.target instanceof Element
        ? event.target.closest('a[href^="#"]')
        : null;
    const hash = link?.getAttribute("href");
    // A different hash will raise hashchange; only a repeated one needs help.
    if (hash && hash.length > 1 && hash === window.location.hash) follow(hash);
  };
  fromLocation();
  window.addEventListener("hashchange", fromLocation);
  document.addEventListener("click", fromClick);
  return () => {
    window.removeEventListener("hashchange", fromLocation);
    document.removeEventListener("click", fromClick);
  };
}
