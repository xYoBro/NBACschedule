import pdfplumber
import re
from datetime import datetime
import json
from ics import Calendar, Event

# Function to clean and normalize text
def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

# Function to normalize date
def normalize_date(date_str):
    try:
        return datetime.strptime(date_str, '%A %B %d, %Y').strftime('%Y-%m-%d')
    except ValueError:
        cleaned_date = re.sub(r'\s+', ' ', date_str.replace(' ,', ',').strip())
        cleaned_date = re.sub(r'(\w)\s+(\w)', r'\1\2', cleaned_date)  # Merge split words
        try:
            return datetime.strptime(cleaned_date, '%A %B %d, %Y').strftime('%Y-%m-%d')
        except ValueError:
            print(f"Unable to parse date: {date_str}")
            return None

# Function to normalize time
def normalize_time(time_str):
    try:
        start_time, end_time = time_str.split("–")
        start_time_24h = datetime.strptime(start_time.strip(), "%I:%M %p").strftime("%H:%M")
        end_time_24h = datetime.strptime(end_time.strip(), "%I:%M %p").strftime("%H:%M")
        return start_time_24h, end_time_24h
    except ValueError:
        print(f"Unable to parse time: {time_str}")
        return None, None

# Function to extract events from the PDF using pdfplumber
def extract_events_from_pdf(pdf_path):
    events = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")
            current_date = None
            current_location = None

            for line in lines:
                line = clean_text(line)

                # Check for date
                date_match = re.search(r'([A-Z]+\s+[A-Z]+\s+\d{1,2},\s*\d{4})', line)
                if date_match:
                    current_date = normalize_date(date_match.group(0))
                    continue

                # Check for location
                location_match = re.search(r'@ ([A-Za-z \–]+)', line)
                if location_match:
                    current_location = clean_text(location_match.group(1))
                    continue

                # Check for event (time and group)
                time_match = re.findall(r'(\d{1,2}:\d{2}\s*(?:am|pm)\s*–\s*\d{1,2}:\d{2}\s*(?:am|pm))', line)
                group_match = re.search(r':\s*([A-Z]{1,3}[0-9]{0,2}(?:\s*/\s*[A-Z]{1,3}[0-9]{0,2})?)', line)

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

# Function to generate ICS file from events
def generate_ics(events, output_file='practice_schedule.ics'):
    cal = Calendar()

    for event_data in events:
        event = Event()
        event.name = f"{event_data['group']} Practice"
        event.begin = f"{event_data['date']} {event_data['start_time']}"
        event.end = f"{event_data['date']} {event_data['end_time']}"
        event.location = event_data['location']
        cal.events.add(event)

    with open(output_file, 'w') as ics_file:
        ics_file.writelines(cal)
    print(f"ICS file created at {output_file}")

# Main script execution
pdf_file_path = 'path_to_your_pdf.pdf'  # Replace with your PDF file path
events = extract_events_from_pdf(pdf_file_path)

# Output events to JSON (optional)
with open('practice_schedule.json', 'w') as json_file:
    json.dump(events, json_file, indent=4)
print("Events saved to practice_schedule.json")

# Generate ICS file
generate_ics(events)
