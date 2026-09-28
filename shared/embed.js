// Inside an iframe, tell the parent page how tall this page is, so it can size the frame to fit
// (the parent listens for {type: "sama-lab:height"}). Standalone, this does nothing.
export function reportHeight() {
  if (window.parent === window) return;
  document.documentElement.classList.add("embedded");
  const send = () =>
    window.parent.postMessage({ type: "sama-lab:height", height: document.documentElement.scrollHeight, path: location.pathname }, "*");
  new ResizeObserver(send).observe(document.body);
  send();
}
