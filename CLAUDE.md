# NBACschedule — Project Truth

A single-file, zero-backend web app: parents drop the club's weekly practice PDF on
`index.html`, review every parsed practice against a screenshot of its PDF line, and
download an `.ics`. No server, no build step, no dependencies beyond pdf.js from a CDN
(cached for offline by `sw.js`). Hosted via GitHub Pages from `main`.

The old Python pipeline (`convert.py` + venvs) is retired; it lives only in git history
(pre-2026-08-24 commits).

## Wayfinder

| Task | Entry point |
| --- | --- |
| Pool names/aliases/addresses, known groups, default settings | `DEFAULTS` block, top of the script in `index.html` (section 1) |
| PDF parsing / format drift | `index.html` section 4 (`RE` regexes, `parseAll`) |
| Error/typo checks & flags | `parseAll` (per-line) and `applyPicks` (cross-practice) |
| Week-over-week diff | section 5 (`computeDiff`, `rememberImport`) |
| ICS output | section 8 (`buildIcs`) |
| Share link / persistence | section 2 (`picksFromHash`, `LS` keys) |
| Offline caching | `sw.js` |
| Synthetic test PDF | `tools/make_test_pdf.py` (needs reportlab) |

## Hot Zones

- **`RE` regex block + `parseAll` (index.html §4):** the parser IS the product; a wrong
  edit silently drops practices. After any change, run `tools/make_test_pdf.py` and
  verify all 7 slots and every seeded error flag still appear.
- **`buildIcs` (§8):** output must stay RFC 5545-valid (CRLF, 75-octet folding,
  VTIMEZONE) or calendar apps import silently-wrong times. UID scheme is what makes
  re-imports update instead of duplicate — never change `uidFor` casually.
- **`LS` localStorage keys (§2):** renaming a key orphans every parent's saved picks
  and week-over-week memory.
- **`sw.js`:** own-origin fetches are network-first *by design* so deploys propagate
  without a cache-version bump. Making them cache-first would freeze parents on stale
  versions.

## Verification

No test framework — verification is: serve the repo dir, drop `test-week.pdf`
(from `tools/make_test_pdf.py`) on the page, confirm 7 practices parse and the seeded
errors (N0-with-zero, end-before-start, CH2/CH4 split, before-start-date) are all
flagged, then download and eyeball the `.ics`. A real club PDF is the only true test
of format drift.
