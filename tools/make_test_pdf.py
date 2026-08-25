"""Generate a synthetic weekly-schedule PDF in the club's format, seeded with the
human errors index.html's checker is supposed to catch (N0-with-a-zero, an
end-before-start time, a combined CH2/CH4 line, practices before a group's start
date). Drop the output on index.html and every one of those should be flagged.

Usage:  python3 tools/make_test_pdf.py [out.pdf]     (needs: pip install reportlab)
"""
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

OUT = sys.argv[1] if len(sys.argv) > 1 else "test-week.pdf"

LINES = [
    "NBAC SWIMMERS' SCHEDULE (AUGUST 25 - AUGUST 31, 2025)",
    "",
    "MONDAY, AUGUST 25, 2025",
    "@ MEADOWBROOK:",
    "4:00-5:30pm: CH2",
    "5:30-7:00pm: CH4",
    "@ LOYOLA:",
    "6:00-7:30pm: P1",
    "",
    "TUESDAY, AUGUST 26, 2025",
    "@ MEADOWBROOK:",
    "4:00-5:30pm: CH2",
    "",
    "WEDNESDAY, AUGUST 27, 2025",
    "N0 PRACTICES",
    "",
    "THURSDAY, AUGUST 28, 2025",
    "@ GILMAN:",
    "4:00-5:30pm: CH2/CH4",
    "",
    "FRIDAY, AUGUST 29, 2025",
    "@ MEADOWBROOK:",
    "5:30-4:00pm: CH4",
    "",
    "START DATES",
    "CH1, CH2: SEPTEMBER 2, 2025",
    "IM1: SEPTEMBER 8, 2025",
]

c = canvas.Canvas(OUT, pagesize=letter)
_, h = letter
t = c.beginText(inch, h - inch)
t.setFont("Helvetica-Bold", 14)
for ln in LINES:
    t.textLine(ln)
c.drawText(t)
c.showPage()
c.save()
print(f"wrote {OUT}")
