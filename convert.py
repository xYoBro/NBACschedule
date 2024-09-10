import re
from datetime import datetime
import json
from rapidfuzz import fuzz, process  # Use rapidfuzz for fuzzy matching
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import PyPDF2

# Updated regex patterns
date_pattern = r'([A-Z]+\s+[A-Z]+\s+\d{1,2}\s*,\s*\d{4})'
time_pattern = r'(\d{1,2}:\d{2}\s*(?:am|pm)\s*–\s*\d{1,2}:\d{2}\s*(?:am|pm))'
location_pattern = r'@ ([A-Za-z \–]+)'  # Handles spaces and special characters like en-dash
group_pattern = r':\s*([A-Z]{1,3}[0-9]{0,2}(?:\s*/\s*[A-Z]{1,3}[0-9]{0,2})?)'  # Improved group detection

# Define possible locations and groups to allow for fuzzy matching
known_locations = ["GILMAN", "GOUCHER", "LOYOLA UNIVERSITY", "COPPERMINE – BEL AIR"]
known_groups = ["P2", "CH3", "D3", "IM3", "HP1", "P1", "CH1", "CHA", "IMB", "IMA"]

# Function to clean and normalize text for fuzzy matching
def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

# Function to perform fuzzy matching for location or group
def fuzzy_match(query, choices, threshold=80):
    best_match = process.extractOne(query, choices, scorer=fuzz.token_set_ratio)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    return None

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

    # Split by double newline to avoid breaking event details across lines
    lines = text.split("\n\n")

    for line in lines:
        line = clean_text(line)  # Clean the line from extra spaces and formatting errors

        # Check for date
        date_match = re.search(date_pattern, line)
        if date_match:
            current_date = normalize_date(date_match.group(0))
            continue

        # Check for location and apply fuzzy matching
        location_match = re.search(location_pattern, line)
        if location_match:
            location_raw = clean_text(location_match.group(1))
            current_location = fuzzy_match(location_raw, known_locations)
            continue

        # Check for event (time and group) and apply fuzzy matching for groups
        time_match = re.findall(time_pattern, line)
        group_match = re.search(group_pattern, line)

        if time_match and group_match and current_date and current_location:
            start_time, end_time = normalize_time(time_match[0])
            group_raw = clean_text(group_match.group(1))
            group = fuzzy_match(group_raw, known_groups)

            if start_time and end_time and group:
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
