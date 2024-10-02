import argparse
import urllib.request
import pypdf
import re
import sqlite3
import pandas as pd
import os

MODE_EXTRACTION = "layout"
MODE_LAYOUT = False

def main(url):
    stats, pdf = fetch_incidents(url)
    if stats == 200:
        incidents = extract_incidents(pdf)
        db = create_db()
        populate_db(db, incidents)
        status(db)
    else:
        print("Unable to fetch data")


def fetch_incidents(url):
    response = urllib.request.urlopen(url)
    with open("./resources/data.pdf", "wb") as file:
        file.write(response.read())
    return response.getcode(), "./resources/data.pdf"


def create_db():
    db_path = "./resources/normanpd.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE incidents (
            incident_time TEXT,
            incident_number TEXT,
            incident_location TEXT,
            incident_nature TEXT,
                incident_ori TEXT
        )
    """)
    con.commit()
    return con

def extract_incidents(pdf_filepath):
    gathered_data = []
    pdf_reader = pypdf.PdfReader(pdf_filepath)
    for page in pdf_reader.pages:
        text = page.extract_text(layout_mode_space_vertically=MODE_LAYOUT, extraction_mode=MODE_EXTRACTION)
        if check_page(page):
            gathered_data.extend(text.split('\n'))
        else:
            print("No Text Found")
    parsed_records = parse_lines(gathered_data)
    df = pd.DataFrame(parsed_records, columns=["incident_time", "incident_number", "incident_location", "incident_nature","incident_ori"])
    return df


def process_line(input_line):
    components = re.split(r'\s{2,}', input_line)
    if not components or components[0].strip() == "":
        return None
    cleaned_components = [comp.strip() for comp in components]
    return complete_pattern_s(cleaned_components)

# Function to ensure the list has at least 5 elements
def complete_pattern_s(pattern_s):
    return pattern_s + [''] * (5 - len(pattern_s))

# Main function that processes the data
def parse_lines(data):
    return [processed for line in data[3:-1]
            if (processed := process_line(line)) is not None]

def check_page(page):
    if(page):
        return True
    return False

def skip_text(line):
    return line.startswith("Daily") or "NORMAN POLICE DEPARTMENT" in line


def process_multiline(lines, line, index):
    list_words = line.split(" ")

    if len(list_words) == 2:
        return list_words  # Malformed line, skip further processing

    if index < len(lines) - 2:
        next_line = lines[index + 1].split(" ")
        if len(next_line) < 7 and len(next_line) > 2:
            list_words += next_line  # Merge the next line into the current one

    return list_words


def populate_db(db, incidents):
    incidents.to_sql('incidents', db, if_exists='replace', index=False)


def status(db):
    cur = db.cursor()
    cur.execute("SELECT incident_nature, COUNT(*) FROM incidents GROUP BY incident_nature ORDER BY incident_nature ASC")
    rows = cur.fetchall()
    db.close()

    for row in rows:
        print(f"{row[0]}|{row[1]}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, help="Incident summary URL.")
    args = parser.parse_args()
    main(args.incidents)