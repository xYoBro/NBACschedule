# NBAC Weekly Schedule → Calendar

One HTML file ([index.html](index.html)). Drop the club's weekly practice PDF on it, pick the groups you care about, check each practice against a screenshot of the PDF line it came from, fix anything the humans got wrong, download an `.ics`, open it in Apple/Google/Outlook Calendar. Nothing is uploaded anywhere — the PDF is read in your browser.

## Sharing it with other parents

This repo is GitHub Pages-ready: Settings → Pages → deploy from `main`, and the page is live at `https://<you>.github.io/NBACschedule/`.

Once hosted, each parent:

- Opens the link, drops the PDF, ticks their groups, types their kid's name next to each.
- Clicks **Share my link** — this copies a URL like `…/#g=P1:Peyton,CH1:Henry`. Bookmark that. Every week after: drop → review → download, no picking.
- Their picks are also remembered by the browser, so the plain link works the same way after the first visit.

The file can also just be emailed or texted around and opened locally; everything works from a `file://` URL too (minus offline caching, which needs http).

## What "check & fix" catches

- Group typos (`PI`, `CHI`, `CH 1`, `Ch-1`) → normalized and flagged; near-misses like `P1A` reported but not added
- Time problems: end before start, missing AM/PM, `4:00 am` typos, unusually short/long practices
- Day-of-week that doesn't match the date, dates outside the week in the title, missing year
- Practices listed before that group's start date (read from the PDF's own start-date list)
- Pool typos matched fuzzily and flagged; unknown pools
- Exact duplicate lines (auto-unchecked), overlapping practices for one swimmer, and two swimmers overlapping at different pools
- Time and group split across two lines, `N0 PRACTICES` with a zero, groups listed together (`P1/CH1`)

Every row is editable, rows can be excluded or removed, and practices can be added by hand.

## Week-over-week

After each download the browser remembers what was exported. The next import shows **New / Changed / Gone** against the last one for the same set of groups, and offers **Download changes only**. Because an `.ics` can't delete events, "Gone" and time-changed practices are listed so you can delete the old ones by hand. Most useful when a *revised* schedule for the same week comes out.

## Settings (gear button)

Calendar name, event title template (`{name}`, `{group}`, `{pool}`), leave-for-practice alert, optional pick-up alert 15 min before the end, sanity thresholds, and pool addresses (these power travel-time alerts and maps). Settings are per-browser; the share link carries only group picks.

## Maintaining it

Everything a maintainer might touch is in the `DEFAULTS` block at the top of the script in `index.html`: pool names/aliases/addresses and the backstop list of group names. Group start dates and the set of groups are read from each PDF automatically.

If the club changes the PDF layout, the parser (section 4 of the script) is where to look. The "Every practice found in the PDF" table at the bottom of the review screen is the canary: if it comes up short one week, the format drifted.

To exercise the parser without a real club PDF, `python3 tools/make_test_pdf.py` (needs `pip install reportlab`) writes `test-week.pdf` — a synthetic schedule seeded with the known human errors. Drop it on the page; every seeded error should be flagged.

## Known limits

- Needs internet on the **first** visit to fetch the PDF reader library (pdf.js from cdnjs, jsdelivr fallback). When served over http(s), a service worker (`sw.js`) then caches the page and libraries, so later visits work offline.
- Can't read scanned/image-only PDFs.
- Time zone is fixed to US Eastern.
- The Bel Air pool address is a placeholder — fix it in Settings.
