import pdfplumber
import re
from datetime import datetime
import json
from ics import Calendar, Event
from tkinter import Tk, Label, Button, Listbox, StringVar, filedialog, SINGLE

# Function to open a file dialog and get the PDF path
def get_pdf_file():
    root = Tk()
    root.withdraw()  # Close the root window
    filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    root.destroy()  # Ensure the root window is closed
    return filename

# Function to clean and normalize text by stripping extra spaces and newlines
def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

# Function to normalize date strings into 'YYYY-MM-DD' format
def normalize_date(date_str):
    try:
        # Convert the month name to title case to handle mixed-case months
        cleaned_date = date_str.title()
        return datetime.strptime(cleaned_date, '%B %d, %Y').strftime('%Y-%m-%d')
    except ValueError:
        cleaned_date = re.sub(r'\s+', ' ', date_str.replace(' ,', ',').strip())
        cleaned_date = re.sub(r'(\w)\s+(\w)', r'\1\2', cleaned_date)  # Merge split words
        try:
            cleaned_date = cleaned_date.title()  # Ensure consistent case for the date string
            return datetime.strptime(cleaned_date, '%B %d, %Y').strftime('%Y-%m-%d')
        except ValueError:
            print(f"Unable to parse date: {date_str}")
            return None

# Function to normalize time range strings into 'HH:MM' 24-hour format
def normalize_time(time_str):
    try:
        start_time, end_time = time_str.split("–")
        start_time_24h = datetime.strptime(start_time.strip(), "%I:%M %p").strftime("%H:%M")
        end_time_24h = datetime.strptime(end_time.strip(), "%I:%M %p").strftime("%H:%M")
        return start_time_24h, end_time_24h
    except (ValueError, AttributeError):
        print(f"Unable to parse time: {time_str}")
        return None, None

# Function to extract events from the PDF using pdfplumber
def extract_events_from_pdf(pdf_path, selected_group):
    events = []
    current_location = None  # Initialize location context

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            print(f"Extracted text from page: {text[:500]}...")  # Debug: Print a snippet of the extracted text
            lines = text.split("\n")
            current_date = None

            for line in lines:
                line = clean_text(line)

                # Date extraction
                date_match = re.search(r'([A-Za-z]+\s+\d{1,2},\s*\d{4})', line)
                if date_match:
                    current_date = normalize_date(date_match.group(0))
                    continue

                # Location extraction (if line starts with '@')
                if '@' in line:
                    location_match = re.search(r'@ ([A-Za-z \-]+)', line)
                    if location_match:
                        current_location = clean_text(location_match.group(1))
                        print(f"Current location updated to: {current_location}")
                    continue

                # Time and group extraction
                time_match = re.findall(r'(\d{1,2}:\d{2}\s*(?:am|pm)[\s–-]*\d{1,2}:\d{2}\s*(?:am|pm))', line)
                group_match = re.search(r':\s*([A-Z]{1,3}[0-9](?:\s*/\s*[A-Z]{1,3}[0-9])?)', line)

                if time_match and group_match and current_date and current_location:
                    start_time, end_time = normalize_time(time_match[0])
                    group = group_match.group(1).strip()

                    # Debug: Print the matched group, start time, end time, and location
                    print(f"Matched group: {group}, Start time: {start_time}, End time: {end_time}, Location: {current_location}")

                    # Only include events for the selected group
                    if start_time and end_time and group == selected_group:
                        event = {
                            "date": current_date,
                            "location": current_location,
                            "group": group,
                            "start_time": start_time,
                            "end_time": end_time
                        }
                        events.append(event)

    # Debug: Print the final events extracted
    print(f"Events extracted: {events}")
    return events

# Function to generate an ICS file from the list of events
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

# Function to create a Tkinter UI for selecting the group from a list
def select_group():
    def submit_selection():
        selected_value = group_listbox.get(group_listbox.curselection())
        root.quit()  # Exit the Tkinter main loop
        root.destroy()  # Close the popup window
        run_script_with_selection(selected_value)

    root = Tk()
    root.title("Select Group")

    group_var = StringVar()

    Label(root, text="Select Group for Event Extraction").pack(pady=10)

    group_listbox = Listbox(root, listvariable=group_var, selectmode=SINGLE, height=6)
    group_listbox.pack(pady=10)

    # Available groups for selection
    available_groups = ["CH2", "CH4", "P1", "P2", "IM3", "IM4", "IM5", "D1", "D2", "CHA", "IMB", "IMA"]
    for group in available_groups:
        group_listbox.insert("end", group)

    Button(root, text="Submit", command=submit_selection).pack(pady=10)

    root.mainloop()

# Function to run the main script with the selected group
def run_script_with_selection(selected_group):
    pdf_file_path = get_pdf_file()
    if pdf_file_path:
        events = extract_events_from_pdf(pdf_file_path, selected_group)

        # Output events to JSON (optional)
        with open('practice_schedule.json', 'w') as json_file:
            json.dump(events, json_file, indent=4)
        print("Events saved to practice_schedule.json")

        # Generate ICS file
        generate_ics(events)
    else:
        print("No PDF file selected.")
    exit()  # Ensure the script exits cleanly after processing

# Start the script by opening the group selection UI
select_group()
