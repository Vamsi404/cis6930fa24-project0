import argparse
import urllib.request
from urllib.request import urlopen,urlretrieve
import pypdf
from pypdf import PdfReader
import sqlite3
from sqlite3 import Error
import re
import os
os.makedirs('./tmp', exist_ok=True)

# Download the PDF if it doesn't exist
def download_pdf(url, save_path):
    if not os.path.isfile(save_path):
        print(f"Initiating download from {url}...")
        try:
            urlretrieve(url, save_path)
            print(f"Download complete. PDF saved at {save_path}")
        except Exception as error:
            print(f"Error during download: {error}")
            raise


#establish connection to sqlite and create incidents table if not present
def create_database():
    try:
        connection = sqlite3.connect('./resources/normanpd.db')
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS incidents (
                    incident_time TEXT, incident_number TEXT, incident_location TEXT, nature TEXT, incident_ori TEXT)''')
        return connection
    except Error as err:
        print(f"Database error: {err}")
        return None


#insert formatted pdf data into DBs
def populate_database(connection, data):
    cursor = connection.cursor()
    cursor.execute('DELETE FROM incidents')
    cursor.executemany('INSERT INTO incidents (incident_time, incident_number, incident_location, nature, incident_ori) VALUES (?,?,?,?,?)', data)
    connection.commit()


#Print Nature|Count(*)
def display_status(connection):
    cursor = connection.cursor()
    cursor.execute('''SELECT nature, COUNT(*) AS event_count 
                      FROM incidents 
                      GROUP BY nature 
                      ORDER BY event_count DESC, nature ASC''')
    records = cursor.fetchall()
    for record in records:
        print(f"{record[0]} | {record[1]}")



def get_last_capital_segment(string):
    result = re.search(r'[A-Z][a-z]+$|(MVA|COP|EMS|DDACTS|911)$', string)

    if result:
        return result.group()
    else:
        return ""


#Split pdf string data by newline and then format each row of pdf to get the required values
def extract_incidents():
    pdf_reader = PdfReader("./tmp/Incident_Report.pdf")
    incidents_list = []
    lines_list = []
    
    for page in pdf_reader.pages:
        lines_list += (page.extract_text()
                          .replace("NORMAN", "")
                          .replace("POLICE", "")
                          .replace("DEPARTMENT", "")
                          .split('\n'))

    # Remove the last line containing the date only
    lines_list.pop()

    for i in range(len(lines_list)):
        current_line = lines_list[i].strip().split(' ')
        incident = []
        line_length = len(current_line)

        if i == 0 or current_line[0] == "Daily":
            continue

        if line_length < 6 and not re.match(r".*?/.*?/.*?", current_line[0]):
            incidents_list.pop()
            # If the incident information is split across two lines, extract location and nature separately
            split_nature = lines_list[i].strip().split(' ')
            for j in range(len(split_nature)):
                previous_text = split_nature[j]
                split_nature[j] = get_last_capital_segment(previous_text)
                
                # Stop at the first occurrence of nature text
                if previous_text != split_nature[j] and split_nature[j] != "":
                    break

            current_line = lines_list[i-1].strip().split(' ') + split_nature
            line_length = len(current_line)
        
        incident_time = current_line[0] + ' ' + current_line[1]
        incident_number = current_line[2]
        incident_ori = current_line[line_length - 1]
        
        incident.append(incident_time)
        incident.append(incident_number)
        
        if line_length < 5:
            incident_location = ""
        else:
            incident_location = current_line[3] + ' '
        
        incident_nature = ""
        is_nature = False
        
        # Constructing the incident location and nature, handling edge cases
        for j, segment in enumerate(current_line):
            if j == line_length - 1 or segment == "":
                continue

            if is_nature:
                incident_nature += segment + ' '
                continue
            
            if j >= 4:
                if segment.isdigit():
                    if segment == "911":
                        is_nature = True
                        incident_nature += segment + ' '
                    else:
                        incident_location += segment + ' '
                elif (segment in ["MVA", "COP", "DDACTS", "EMS"] or not segment.isupper()) and segment not in ['/'] and not re.match(r"^\d{1}/\d{1}", segment):
                    is_nature = True
                    incident_nature += segment + ' '
                else:
                    incident_location += segment + ' '

        incident.append(incident_location.strip())
        incident.append(incident_nature.strip())
        incident.append(incident_ori)
        incidents_list.append(incident)

    # Convert to a list of tuples
    incidents_tuples = [tuple(incident) for incident in incidents_list]
    return incidents_tuples

def main(url):
    # Step 1: Download the PDF data
    download_pdf(url, "./tmp/Incident_Report.pdf")
    
    # Step 2: Extract the incidents from the PDF
    incidents_data = extract_incidents()
    # print(incidents_data)
    
    # Step 3: Create a new SQLite database
    connection = create_database()

    # Step 4: Populate the database with extracted data
    populate_database(connection, incidents_data)
    
    # Step 5: Display the status of incident counts
    display_status(connection)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)