import argparse
import urllib.request
import pypdf
import sqlite3
import re
import os

# Ensure necessary directories exist
os.makedirs('./tmp', exist_ok=True)

# Download the PDF if it doesn't exist
def download_pdf(url, save_path):
    if not os.path.isfile(save_path):
        try:
            print(f"Downloading PDF from {url}...")
            urllib.request.urlretrieve(url, save_path)
            print(f"PDF saved at {save_path}")
        except Exception as error:
            print(f"Failed to download the PDF: {error}")
            raise

# Set up the database and create the incidents table
def create_database():
    db_path = './resources/normanpd.db'
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS incidents (
            incident_time TEXT,
            incident_number TEXT,
            incident_location TEXT,
            nature TEXT,
            incident_ori TEXT
        )''')
        return connection
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

# Insert incidents into the database
def populate_database(connection, incidents):
    try:
        cursor = connection.cursor()
        cursor.executemany('INSERT INTO incidents (incident_time, incident_number, incident_location, nature, incident_ori) VALUES (?,?,?,?,?)', incidents)
        connection.commit()
    except sqlite3.Error as e:
        print(f"Failed to populate the database: {e}")

# Display the counts of each type of incident
def display_status(connection):
    cursor = connection.cursor()
    cursor.execute('SELECT nature, COUNT(*) FROM incidents GROUP BY nature ORDER BY nature ASC')
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}|{row[1]}")

# Skip unnecessary lines such as headings or non-relevant content
def skip_line(line):
    return any(keyword in line for keyword in ["NORMAN POLICE DEPARTMENT", "Daily", "Incident Log"])

# Extract incidents from the PDF file
def extract_incidents(pdf_path):
    pdf_reader = pypdf.PdfReader(pdf_path)
    incidents = []
    
    for page in pdf_reader.pages:
        content = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False,
                                               layout_mode_scale_weight=2.0)
        if content:
            lines = content.split("\n")
            for line in lines:
                if skip_line(line) or not line.strip():
                    continue
                
                # Use regular expressions to split the line into components
                data = re.split(r'\s{2,}', line.strip())
                if len(data) >= 3:
                    incident_time = data[0]
                    incident_number = data[1]
                    incident_location = data[2] if len(data) > 3 else ''
                    incident_nature = data[3] if len(data) > 4 else ''
                    incident_ori = data[-1]  # Last item is usually the incident ORI
                    incidents.append((incident_time, incident_number, incident_location, incident_nature, incident_ori))
    
    return incidents

def main(url):
    pdf_path = './tmp/Incident_Report.pdf'
    
    # Step 1: Download the PDF
    download_pdf(url, pdf_path)
    
    # Step 2: Extract incidents from the downloaded PDF
    incidents = extract_incidents(pdf_path)
    if not incidents:
        print("No incidents extracted.")
    else:
        print(f"Extracted {len(incidents)} incidents.")
        print(incidents[:5])  # Print the first 5 incidents as a sample
    
    
    # Step 3: Set up the database
    connection = create_database()
    if not connection:
        return

    # Step 4: Populate the database with extracted data
    populate_database(connection, incidents)
    
    # Step 5: Display incident types and counts
    display_status(connection)
    
    connection.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--incidents', type=str, required=True, help='URL of the incident PDF file')
    args = parser.parse_args()
    
    main(args.incidents)
