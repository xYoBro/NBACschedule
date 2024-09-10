import PyPDF2
import re
import json
from ics import Calendar, Event
from datetime import datetime
from fuzzywuzzy import process
from spellchecker import SpellChecker
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# List of known groups and locations for fuzzy matching and validation
KNOWN_GROUPS = ["CH2", "CH3", "IM2", "IM3", "P1", "P2", "D1", "D2", "CHA", "IMB", "HP1", "HP2"]
KNOWN_LOCATIONS = ["GILMAN", "GOUCHER", "LOYOLA UNIVERSITY", "COPPERMINE – BEL AIR"]

# Set up a spell checker for detecting common mistakes
spell = SpellChecker()

# Hide the root Tkinter window
Tk().withdraw()

# Open a file dialog to select the PDF file
pdf_path = askopenfilename(title="Select the Practice Schedule PDF", filetypes=[("PDF files", "*.pdf")])

# Check if a file was selected
if not pdf_path:
    print("No file selected. Exiting...")
    exit()

# Read the PDF content
with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()

# Print the extracted text to check its structure
print("Extracted text from PDF:")
print(text)

# Example regular expression matching practice schedule entries
schedule_entries = re.findall(r'([A-Z]+DAY.*?)(?=[A-Z]+DAY|$)', text, re.DOTALL)

# Initialize JSON data
json_data = []

# Function to convert 12-hour time format to 24-hour format
def convert_time(time_str):
    # Normalize time format, handle missing AM/PM and spacing issues
    match = re.match(r'(\d{1,2}):(\d{2})\s*([APM]+)?', time_str.strip())
    if match:
        hour, minute, period = int(match.group(1)), match.group(2), match.group(3)
        if period and period.upper() == 'PM' and hour != 12:
            hour += 12
        elif period and period.upper() == 'AM' and hour == 12:
            hour = 0
        return f'{hour:02}:{minute}'
    return time_str

# Function to clean and normalize date strings by removing extra spaces and handling common issues
def normalize_date(date_str):
    # Remove extra spaces, fix common issues like misplaced spaces in the date
    date_str = re.sub(r'\s+', ' ', date_str).strip()  # Remove extra spaces
    date_str = re.sub(r'(\d{1,2})\s(\d{1,2}),', r'\1\2,', date_str)  # Fix spaces in day number (e.g., "1 5" -> "15")
    date_str = re.sub(r'([A-Za-z]+)\s+(\d{1,2})\s*,\s*(\d{4})', r'\1 \2, \3', date_str)  # Fix misplaced spaces
    date_str = date_str.title()  # Ensure capitalization is consistent (e.g., "September")
    
    try:
        return datetime.strptime(date_str, '%A %B %d, %Y')
    except ValueError:
        # Attempt a fallback fix if there are still issues
        corrected_date_str = re.sub(r'(\w+day)\s+', r'\1 ', date_str)  # Fix potential spacing issues in the day of the week
        try:
            return datetime.strptime(corrected_date_str, '%A %B %d, %Y')
        except ValueError:
            print(f"Unable to correct the date string: {date_str}")
            return None  # Return None for logging or manual correction

# Function to normalize group names using fuzzy matching
def normalize_group(group_str):
    group_str = group_str.strip()
    # Use fuzzy matching to correct group names
    best_match = process.extractOne(group_str, KNOWN_GROUPS)
    return best_match[0] if best_match else group_str

# Function to normalize location names using fuzzy matching
def normalize_location(location_str):
    location_str = location_str.strip()
    best_match = process.extractOne(location_str, KNOWN_LOCATIONS)
    return best_match[0] if best_match else location_str

# Parse each schedule entry and convert to JSON structure
for entry in schedule_entries:
    lines = entry.split('\n')
    current_date = normalize_date(lines[0].strip())  # First line contains the date
    if current_date is None:
        print(f"Skipping unparseable date: {lines[0].strip()}")
        continue  # Skip unparseable dates
    
    location = None

    for line in lines[1:]:
        line = line.strip()

        if '@' in line:
            location = normalize_location(line.split('@')[1].strip())  # Get the location and normalize
        elif re.match(r'\d{1,2}:\d{2}\s?[APM]+', line):  # Matches time lines
            time_match = re.findall(r'(\d{1,2}:\d{2}\s?[APM]+)', line)
            group_match = re.findall(r'[A-Z0-9\s]+$', line)
            if len(time_match) == 2 and location:
                start_time = convert_time(time_match[0])
                end_time = convert_time(time_match[1])
                group = normalize_group(group_match[0].strip() if group_match else "Unknown")
                
                # Append structured data as JSON
                json_data.append({
                    "date": current_date.strftime('%A %B %d, %Y'),
                    "location": location,
                    "group": group,
                    "start_time": start_time,
                    "end_time": end_time
                })

# Save JSON data to a file
json_file_path = 'practice_schedule.json'
with open(json_file_path, 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

print(f"JSON data saved at {json_file_path}")

# Now, convert JSON to ICS
cal = Calendar()

# Parse the JSON data to create ICS events
for event_data in json_data:
    title = f"Practice {event_data['group']} at {event_data['location']}"
    event_date = event_data['date']

    try:
        # Combine date and time for start and end times
        event_date_obj = datetime.strptime(event_date, '%A %B %d, %Y')
        start_datetime = datetime.combine(event_date_obj, datetime.strptime(event_data['start_time'], '%H:%M').time())
        end_datetime = datetime.combine(event_date_obj, datetime.strptime(event_data['end_time'], '%H:%M').time())
        
        # Create an ICS event
        event = Event()
        event.name = title
        event.begin = start_datetime
        event.end = end_datetime
        event.location = event_data['location']
        
        # Add the event to the calendar
        cal.events.add(event)

    except ValueError as e:
        print(f"Error parsing date or time for event: {event_data}")
        print(f"Error: {e}")

# Save the ICS calendar to a file
ics_file_path = 'practice_schedule.ics'
with open(ics_file_path, 'w') as ics_file:
    ics_file.writelines(cal)

print(f"ICS file created at {ics_file_path}")
