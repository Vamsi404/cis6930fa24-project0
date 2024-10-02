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
                      ORDER BY nature ASC''')
    records = cursor.fetchall()
    for record in records:
        print(f"{record[0]}|{record[1]}")



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

    for page in pdf_reader.pages:
        content = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False,
                                               layout_mode_scale_weight=2.0)
        lines = content.split("\n")
        
        for line in lines:
            if line.startswith("    "):  # Skip headings or conclusions
                continue
            
            # Split the line based on 4 or more spaces
            data_array = [e.strip() for e in re.split(r"\s{4,}", line.strip())]
            
            # Check the structure of the data
            if len(data_array) == 5:
                # Full incident information
                incident_time = data_array[0]
                incident_number = data_array[1]
                incident_location = data_array[2]
                incident_nature = data_array[3]
                incident_ori = data_array[4]
                incident = (incident_time, incident_number, incident_location, incident_nature, incident_ori)
                incidents_list.append(incident)
            elif len(data_array) == 3:
                # Incident information might be split
                incident_time = data_array[0]
                incident_number = data_array[1]
                incident_location = ""
                incident_nature = ""
                incident_ori = data_array[2]
                incident = (incident_time, incident_number, incident_location, incident_nature, incident_ori)
                incidents_list.append(incident)

    # Convert to a list of tuples
    # incidents_tuples = [tuple(incident) for incident in incidents_list]
    return incidents_list

def main(url):
    # Step 1: Download the PDF data
    download_pdf(url, "./resources/Incident_Report.pdf")
    
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