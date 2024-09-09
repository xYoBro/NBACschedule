import PyPDF2
import csv
import re
from ics import Calendar, Event
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from datetime import datetime

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

# Extracting individual entries for practices using regex
schedule_entries = re.findall(r'([A-Z]+DAY.*?)(?=[A-Z]+DAY|$)', text, re.DOTALL)

# Initialize CSV data with headers
csv_data = [['Title', 'Date', 'Start Time', 'End Time', 'Location']]

# Function to convert 12-hour time format to 24-hour format
def convert_time(time_str):
    match = re.match(r'(\d+):(\d+)\s*([APM]+)', time_str)
    if match:
        hour, minute, period = int(match.group(1)), match.group(2), match.group(3)
        if period == 'PM' and hour != 12:
            hour += 12
        elif period == 'AM' and hour == 12:
            hour = 0
        return f'{hour:02}:{minute}'
    return time_str

# Parse each entry and extract only CH2 events
for entry in schedule_entries:
    lines = entry.split('\n')
    current_date = lines[0].strip()  # The first line contains the day and date
    location = None
    
    for line in lines[1:]:
        line = line.strip()
        if '@' in line:
            location = line.split('@')[1].strip()  # Update location when found
        elif re.match(r'\d{1,2}:\d{2}\s?[APM]+', line):  # Matches time lines
            # Extract start/end times and group information
            if 'CH2' in line:  # Only include CH2 events
                time_match = re.findall(r'(\d{1,2}:\d{2}\s?[APM]+)', line)
                group_match = re.findall(r'[A-Z0-9]+', line)
                if len(time_match) == 2 and location:
                    start_time = convert_time(time_match[0])
                    end_time = convert_time(time_match[1])
                    title = f"Practice CH2 at {location}"
                    
                    # Format the data for CSV
                    csv_data.append([title, current_date, start_time, end_time, location])

# Write to CSV
csv_file_path = 'ch2_practice_schedule.csv'
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print(f"CSV file created at {csv_file_path}")

# Create a new calendar
cal = Calendar()

# Open the CSV and parse each event
with open(csv_file_path, mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row
    
    for row in reader:
        title, date_str, start_time_str, end_time_str, location = row
        
        # Parse the date and time
        try:
            event_date = datetime.strptime(date_str, '%A %B %d, %Y')
        except ValueError:
            print(f"Error parsing date: {date_str}")
            continue
            
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        
        # Combine date and time to create datetime objects
        start_datetime = datetime.combine(event_date, start_time)
        end_datetime = datetime.combine(event_date, end_time)
        
        # Create a new event
        event = Event()
        event.name = title
        event.begin = start_datetime
        event.end = end_datetime
        event.location = location
        
        # Add the event to the calendar
        cal.events.add(event)

# Save the calendar as an ICS file
ics_file_path = 'ch2_practice_schedule.ics'
with open(ics_file_path, 'w') as ics_file:
    ics_file.writelines(cal)

print(f"ICS file created at {ics_file_path}")
