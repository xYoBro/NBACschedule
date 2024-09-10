import re
from datetime import datetime
import json
from fuzzywuzzy import fuzz
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import PyPDF2

# Regex patterns to match different components
date_pattern = r'([A-Z]+\s+[A-Z]+\s+\d{1,2}\s*,\s*\d{4})'
time_pattern = r'(\d{1,2}:\d{2}\s*(?:am|pm)\s*–\s*\d{1,2}:\d{2}\s*(?:am|pm))'
location_pattern = r'@ ([A-Z ]+)'
group_pattern = r':\s*([A-Z]{1,3}[0-9]?)'  # Improved pattern to match groups like "P2", "CH3", "D3", etc.

# Function to open a file dialog and get the PDF path
def get_pdf_file():
    Tk().withdraw()  # Close the root window
    filename = askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return filename

# Function to extract text from the selected PDF file
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def normalize_date(date_str):
    try:
        return datetime.strptime(date_str, '%A %B %d, %Y').strftime('%Y-%m-%d')
    except ValueError:
        cleaned_date = re.sub(r'\s+', ' ', date_str).replace(' ,', ',')
        try:
            return datetime.strptime(cleaned_date, '%A %B %d, %Y').strftime('%Y-%m-%d')
        except ValueError as e:
            print(f"Unable to parse date: {date_str}")
            return None

def normalize_time(time_str):
    try:
        start_time, end_time = time_str.split("–")
        start_time_24h = datetime.strptime(start_time.strip(), "%I:%M %p").strftime("%H:%M")
        end_time_24h = datetime.strptime(end_time.strip(), "%I:%M %p").strftime("%H:%M")
        return start_time_24h, end_time_24h
    except ValueError as e:
        print(f"Unable to parse time: {time_str}")
        return None, None

def extract_events(text):
    events = []
    current_date = None
    current_location = None

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        # Check for date
        date_match = re.search(date_pattern, line)
        if date_match:
            current_date = normalize_date(date_match.group(0))
            continue

        # Check for location
        location_match = re.search(location_pattern, line)
        if location_match:
            current_location = location_match.group(1).strip()
            continue

        # Check for event (time and group)
        time_match = re.findall(time_pattern, line)
        group_match = re.search(group_pattern, line)

        if time_match and group_match and current_date and current_location:
            start_time, end_time = normalize_time(time_match[0])
            group = group_match.group(1).strip()

            if start_time and end_time:
                event = {
                    "date": current_date,
                    "location": current_location,
                    "group": group,
                    "start_time": start_time,
                    "end_time": end_time
                }
                events.append(event)
    return events

# Prompt for the PDF file containing the schedule
pdf_file_path = get_pdf_file()

if pdf_file_path:
    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(pdf_file_path)

    # Extract events from the text
    events = extract_events(extracted_text)

    # Save the extracted events to a JSON file
    json_file_path = 'practice_schedule.json'
    with open(json_file_path, 'w') as json_file:
        json.dump(events, json_file, indent=4)

    print(f"JSON data saved at {json_file_path}")

    # Generate ICS format
    def generate_ics(events):
        from ics import Calendar, Event

        cal = Calendar()

        for event_data in events:
            event = Event()
            event.name = f"{event_data['group']} Practice"
            event.begin = f"{event_data['date']} {event_data['start_time']}"
            event.end = f"{event_data['date']} {event_data['end_time']}"
            event.location = event_data['location']
            cal.events.add(event)

        # Save the calendar to a file
        ics_file_path = 'practice_schedule.ics'
        with open(ics_file_path, 'w') as ics_file:
            ics_file.writelines(cal)

        print(f"ICS file created at {ics_file_path}")

    # Generate ICS file from the extracted events
    generate_ics(events)
else:
    print("No PDF file selected.")
