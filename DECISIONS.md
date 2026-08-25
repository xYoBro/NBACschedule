# DECISIONS

Index: D1 single-file HTML app replaces Python pipeline · D2 share-link-as-config, no
config file · D3 GitHub Pages + service worker · D4 .ics download, no subscription feed

---

**D1 (2026-08-24) — The app is one static HTML file; the Python pipeline is retired.**
`convert.py` hard-coded two groups, had no error surfacing, needed a local Python env,
and titled every event "Edit here to sign up". `index.html` is zero-install, shareable,
shows PDF evidence per event, and checks for the schedule's human errors. Verified
end-to-end against a synthetic club-format PDF before adoption. Cost to learn: two
committed venvs (~3,000 files) and months of manually re-run scripts.

**D2 (2026-08-24) — Per-parent config travels in the share-link hash (`#g=...`) plus
localStorage; there is no downloadable config file.** A config file would have to be
downloaded, kept track of, and re-uploaded — file management is exactly the friction
parents on phones won't tolerate. A URL is already a config file: bookmarkable,
textable, survives hosting moves. "Preferred calendar" doesn't belong in config at all:
the .ics is universal, and the post-download hint adapts to the device instead. Rewind
seam if this is ever wrong: `picksFromHash`/`hashFromPicks` are the only serialization
points — a file import/export would slot in beside them.

**D3 (2026-08-24) — Hosted as `index.html` on GitHub Pages; `sw.js` caches the page
and CDN libraries for offline.** Own-origin = network-first (deploys propagate without
cache-version bumps), CDN = cache-first (versioned URLs). First visit still needs
internet.

**D4 (2026-08-24) — Calendar delivery stays a downloaded .ics, not a subscription
(webcal) feed.** A feed would auto-update and auto-delete events — strictly better UX —
but requires a server holding every family's schedule, which this project deliberately
does not have. Revisit only if a backend ever becomes acceptable.
