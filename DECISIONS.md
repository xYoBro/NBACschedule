# DECISIONS

Index: D1 single-file HTML app replaces Python pipeline · D2 share-link-as-config, no
config file · D3 GitHub Pages + service worker · D4 .ics download, no subscription feed
· D5 one adaptive download button, no per-service button row

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
does not have. Revisit only if a backend ever becomes acceptable. If revisited, the
best shape is per-GROUP feeds (no personal data server-side): one maintainer drops the
weekly PDF and publishes; every other family subscribes via webcal once and never
touches the app again.

**D5 (2026-08-24) — One adaptive download button, not an Apple/Outlook/Google button
row.** Direct insertion is impossible: no web API exists for Apple Calendar or bulk
Outlook import, and Google/Outlook URL schemes take one event per click — so every
"add to calendar" button any site shows is the same .ics with different labeling.
Given that, per-service buttons only add a choice the device can make itself: the UA
picks the label ("Download for Apple Calendar" on Mac/iOS, "for Outlook" on Windows)
and the post-download instructions, with a Google import link where relevant. The
`PLATFORM` object in index.html §8 is the single seam if buttons are ever wanted.
*Amendment (2026-08-24):* an iOS one-tap experiment (window.open on the blob so
QuickLook shows "Add All" instead of saving) was shipped and reverted the same day —
user testing still got a download, and the owner ruled the extra code fork not worth
it. Every platform uses the same plain download; don't retry the handoff trick
without a device-verified proof first.
