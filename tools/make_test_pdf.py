"""Generate a synthetic weekly-schedule PDF mirroring the club's real format
(verified against the actual 2026-08-24 schedule: day headers without a comma
after the weekday, "@POOL" with and without a space, " pm – " separators with a
colon before the group, START DATES with weekday names, stroke-clinic/NOTE/SAVE
THE DATE sections that must be ignored) — seeded with the human errors
index.html's checker is supposed to catch.

Expected when dropped on index.html: 7 practices (Mon 3, Tue 1, Thu 2 from the
combined CH2/CH4 line, Fri 1), week range Aug 24-30 2026, start dates for
CH1/CH2/IM1/IM2, and flags for: N0-with-a-zero (1 note), CH2 before its start
date (Mon+Tue, warn), AM/PM printed once (Tue+Fri, info), end-before-start
rescued to AM + unusually-long (Fri, warn x2). Nothing from the trailing
sections may parse as a practice.

Usage:  python3 tools/make_test_pdf.py [out.pdf]     (needs: pip install reportlab)
"""
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

OUT = sys.argv[1] if len(sys.argv) > 1 else "test-week.pdf"

LINES = [
    "2026 – 2027",
    "NORTH BALTIMORE AQUATIC CLUB",
    "PRACTICE SCHEDULE / SWIMMERS",
    "(August 24 - 30, 2026)",
    "",
    "MONDAY AUGUST 24, 2026",
    "@COPPERMINE – MEADOWBROOK",
    "4:00 pm – 5:30 pm:  CH2",
    "5:30 pm – 7:00 pm:  CH4",
    "",
    "@LOYOLA UNIVERSITY",
    "6:00 pm – 7:30 pm:  P1",
    "",
    "TUESDAY AUGUST 25, 2026",
    "@COPPERMINE – MEADOWBROOK",
    "4:00 – 5:30 pm:  CH2",
    "",
    "WEDNESDAY AUGUST 26, 2026",
    "@ GILMAN",
    "N0 PRACTICES",
    "",
    "THURSDAY AUGUST 27, 2026",
    "@ GILMAN",
    "4:00 pm – 5:30 pm:  CH2/CH4",
    "",
    "FRIDAY AUGUST 28, 2026",
    "@COPPERMINE – MEADOWBROOK",
    "5:30 – 4:00 pm:  CH4",
    "",
    "START DATES FOR THE 2026 – 2027 SEASON:",
    "CH1, CH2: Thursday August 27, 2026",
    "IM1, IM2: Monday August 31, 2026",
    "STROKE CLINIC: Monday Sept 14, 2026 @ Coppermine – Bel Air",
    "There will be NO PRACTICES on Sunday September 6, 2026.",
    "NOTE: The schedule may not match your normal schedule yet.",
    "SAVE THE DATE:",
    "SATURDAY SEPTEMBER 12, 2026: NBAC TEAM DAY (11:00 AM – 3:00 PM)",
]

c = canvas.Canvas(OUT, pagesize=letter)
_, h = letter
t = c.beginText(inch, h - inch)
t.setFont("Helvetica-Bold", 12)
for ln in LINES:
    t.textLine(ln)
c.drawText(t)
c.showPage()
c.save()
print(f"wrote {OUT}")
