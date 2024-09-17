import pdfplumber
import re
from datetime import datetime, timedelta
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from tkinter import Tk, filedialog
from icalendar import Calendar, Event, Alarm
import pytz

# Function to open a file dialog and get the PDF path
def get_pdf_file():
    root = Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    root.destroy()
    return filename

# Function to normalize and clean the entire text
def normalize_text(text):
    # Replace various dash characters with a standard hyphen
    text = re.sub(r'[–—−]', '-', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Function to normalize date strings into 'YYYY-MM-DD' format
def normalize_date(date_str):
    try:
        cleaned_date = date_str.strip().title()
        return datetime.strptime(cleaned_date, '%B %d, %Y').strftime('%Y-%m-%d')
    except ValueError:
        print(f"Unable to parse date: {date_str}")
        return None

# Function to normalize time range strings into 'HH:MM' 24-hour format
def normalize_time(time_str):
    try:
        # Normalize the dash character
        time_str = re.sub(r'[–—−]', '-', time_str)
        # Ensure there's a space before 'am' or 'pm'
        time_str = re.sub(r'(\d)([ap]m)', r'\1 \2', time_str, flags=re.IGNORECASE)
        time_str = re.sub(r'\s+', ' ', time_str)  # Remove extra spaces

        start_time_str, end_time_str = time_str.split("-")
        start_time_24h = datetime.strptime(start_time_str.strip(), "%I:%M %p").strftime("%H:%M")
        end_time_24h = datetime.strptime(end_time_str.strip(), "%I:%M %p").strftime("%H:%M")
        return start_time_24h, end_time_24h
    except (ValueError, AttributeError) as e:
        print(f"Unable to parse time: {time_str}")
        return None, None

# Function to extract events from the PDF
def extract_events_from_pdf(pdf_path, selected_group):
    events = []
    current_date = None

    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            full_text += " " + text

        # Normalize the full text
        full_text = normalize_text(full_text)
        print("Extracted Text:")
        print(full_text)

        # Regular expression patterns
        date_pattern = re.compile(r'([A-Za-z]+\s+\d{1,2},\s*\d{4})')

        # Updated event_pattern with non-greedy match and lookahead
        event_pattern = re.compile(
            r'(\d{1,2}:\d{2}\s*(?:am|pm)\s*[-–—−]\s*\d{1,2}:\d{2}\s*(?:am|pm))\s*:\s*([A-Z0-9/ ]+?)(?=\s*\d{1,2}:\d{2}\s*(?:am|pm)|\s*@|\s*(?:MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)|$)',
            re.IGNORECASE
        )

        # Pattern to find locations
        location_pattern = re.compile(r'@ ?([A-Z\s\-\(\)]+)')

        # Find all dates in the text
        date_matches = list(date_pattern.finditer(full_text))
        print(f"Found dates: {[match.group(0) for match in date_matches]}")

        # Iterate over each date and its corresponding text
        for idx, date_match in enumerate(date_matches):
            current_date = normalize_date(date_match.group(0))
            start_idx = date_match.end()

            # Determine the end index for the current date's events
            if idx + 1 < len(date_matches):
                end_idx = date_matches[idx + 1].start()
                date_text = full_text[start_idx:end_idx]
            else:
                date_text = full_text[start_idx:]

            # Find all locations within the date_text
            location_matches = list(location_pattern.finditer(date_text))

            # For each location block
            for loc_idx, loc_match in enumerate(location_matches):
                location_name = loc_match.group(1).strip()
                loc_start_idx = loc_match.end()

                # Determine the end index for this location's events
                if loc_idx + 1 < len(location_matches):
                    loc_end_idx = location_matches[loc_idx + 1].start()
                    loc_text = date_text[loc_start_idx:loc_end_idx]
                else:
                    loc_text = date_text[loc_start_idx:]

                # Find all events within the location text
                for event_match in event_pattern.finditer(loc_text):
                    time_str = event_match.group(1)
                    group = event_match.group(2)
                    # Remove any extra whitespace
                    group = group.strip()
                    print(f"Matched event: time='{time_str}', group='{group}', location='{location_name}'")

                    start_time, end_time = normalize_time(time_str)

                    if start_time and end_time and selected_group == group:
                        event = {
                            "date": current_date,
                            "location": location_name,
                            "group": group,
                            "start_time": start_time,
                            "end_time": end_time
                        }
                        events.append(event)

    return events

# Function to generate a PDF file from the list of events
def generate_pdf(events, output_file):
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    text_object = c.beginText()
    text_object.setTextOrigin(inch, height - inch)
    text_object.setFont("Helvetica", 12)

    if events:
        text_object.textLine(f"Practice Schedule for {events[0]['group']}")
    else:
        text_object.textLine("No events found.")
    text_object.textLine("")

    for event in events:
        text_object.textLine(f"Date: {event['date']}")
        text_object.textLine(f"Time: {event['start_time']} - {event['end_time']}")
        text_object.textLine(f"Location: {event['location']}")
        text_object.textLine("")
    c.drawText(text_object)
    c.showPage()
    c.save()

# Function to generate an .ics file from the list of events with alerts
def generate_ics(events, output_file):
    cal = Calendar()
    cal.add('prodid', '-//NBAC Schedule//mxm.dk//')
    cal.add('version', '2.0')

    # Timezone settings (adjust as needed)
    tz = pytz.timezone('America/New_York')

    for event in events:
        vevent = Event()
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        start_time = datetime.strptime(event['start_time'], '%H:%M').time()
        end_time = datetime.strptime(event['end_time'], '%H:%M').time()

        start_datetime = tz.localize(datetime.combine(event_date, start_time))
        end_datetime = tz.localize(datetime.combine(event_date, end_time))

        vevent.add('dtstart', start_datetime)
        vevent.add('dtend', end_datetime)
        vevent.add('summary', f"Edit here to sign up")
        vevent.add('location', event['location'])
        vevent.add('description', f"Practice for group {event['group']} at {event['location']}.")

        # Optionally, add a unique identifier
        vevent['uid'] = f"{event['date']}_{event['start_time']}_{event['group']}@nbac.com"

        # Create an alarm that triggers 1 hour before the event
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f"Reminder: Practice for {event['group']} at {event['location']} in 1 hour.")
        alarm.add('trigger', timedelta(hours=-1))
        vevent.add_component(alarm)

        cal.add_component(vevent)

    # Write to .ics file
    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())

def main():
    pdf_file_path = get_pdf_file()
    if pdf_file_path:
        groups_to_process = ["CH2", "CH4"]
        for group in groups_to_process:
            events = extract_events_from_pdf(pdf_file_path, group)
            if events:
                # Output events to JSON (optional)
                json_output_file = f'practice_schedule_{group}.json'
                with open(json_output_file, 'w') as json_file:
                    json.dump(events, json_file, indent=4)
                print(f"Events for {group} saved to {json_output_file}")

                # Generate PDF file
                pdf_output_file = f'practice_schedule_{group}.pdf'
                generate_pdf(events, pdf_output_file)
                print(f"PDF file for {group} created at {pdf_output_file}")

                # Generate ICS file
                ics_output_file = f'practice_schedule_{group}.ics'
                generate_ics(events, ics_output_file)
                print(f"ICS file for {group} created at {ics_output_file}")
            else:
                print(f"No events found for group {group}")
    else:
        print("No PDF file selected.")

if __name__ == '__main__':
    main()
