/* Offline cache for index.html and the CDN libraries it needs (pdf.js, fonts).
   Own-origin files: network-first, so a newly deployed page is picked up immediately
   and the cache is only a fallback — no cache-version bump needed on deploy.
   Cross-origin files: cache-first, because those URLs are pinned to a version. */
const CACHE = "nbac-schedule-v1";

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(["./", "./index.html"])).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function cachePut(request, response) {
  if (response && (response.ok || response.type === "opaque"))
    caches.open(CACHE).then(c => c.put(request, response));
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const sameOrigin = new URL(req.url).origin === self.location.origin;
  if (sameOrigin || req.mode === "navigate") {
    e.respondWith(
      fetch(req)
        .then(res => { cachePut(req, res.clone()); return res; })
        .catch(() => caches.match(req, { ignoreSearch: true }).then(hit => hit || caches.match("./index.html")))
    );
  } else {
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => { cachePut(req, res.clone()); return res; }))
    );
  }
});
