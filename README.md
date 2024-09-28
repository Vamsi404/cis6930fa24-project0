
# cis6930fa24 -- Project 0 -- Incident Report Data Analysis

### 🕵️ Name
- Vamsi Manda
- UFID: 43226231
- vmanda@ufl.edu

---

## Project Description

This project extracts incident data from PDFs provided by the Norman, Oklahoma police department, processes the extracted data, and stores it in an SQLite database. The extracted data includes fields such as incident time, number, location, and nature of the incident. The database is then queried to count the number of incidents for each incident type, presenting a summary of the most common occurrences.

---

## How to install
```bash
pipenv install
```

---

## How to run
```bash
pipenv run python3 main.py --incidents url
```
Ensure you have the correct URL for the PDF report passed as an argument.

---

## Functions

#### `main.py`

- **`extractincidents()`**:  
  **Parameters**: None  
  **Process**: Reads the incident report PDF, cleans up and extracts relevant fields (time, number, location, nature, and ori) from each incident entry, and returns the processed data as a list of tuples.  
  **Returns**: A list of incident records, each containing the time, number, location, nature, and ori of the incident.  

- **`download_pdf(url, destination)`**:  
  **Parameters**: `url` (string), `destination` (string)  
  **Process**: Downloads the PDF from the specified URL if it doesn't already exist at the given destination path.  
  **Returns**: None

- **`createdb()`**:  
  **Parameters**: None  
  **Process**: Connects to the SQLite database or creates a new one and initializes the incidents table.  
  **Returns**: A connection object for the SQLite database.

- **`populatedb(conn, incidents)`**:  
  **Parameters**: `conn` (SQLite connection object), `incidents` (list of tuples)  
  **Process**: Clears the existing data in the incidents table, then inserts the new incidents data into the database.  
  **Returns**: None

- **`status(conn)`**:  
  **Parameters**: `conn` (SQLite connection object)  
  **Process**: Queries the database to count the number of incidents for each type (nature) and prints the results sorted by the frequency of events.  
  **Returns**: None

- **`extract_last_capital_onwards(s)`**:  
  **Parameters**: `s` (string)  
  **Process**: Identifies and extracts the last word in the string that starts with an uppercase letter, often used to separate locations from the nature of the incident.  
  **Returns**: A string representing the extracted part of the input.

---

## Database Development

The database for this project is created using SQLite. The `incidents` table is designed with the following fields:
- `incident_time`: The time and date of the incident.
- `incident_number`: A unique identifier for the incident.
- `incident_location`: The reported location of the incident.
- `nature`: The type or nature of the incident (e.g., MVA, COP).
- `incident_ori`: A code representing the agency or origin of the report.

The `createdb()` function checks for the existence of the `incidents` table, creating it if necessary. The `populatedb()` function inserts cleaned data into this table.

---

## Bugs and Assumptions

- **Assumption**: It is assumed that each incident record follows a similar format in the PDF, with fields consistently located in the same position.
- **Bug**: If the incident report format changes significantly (e.g., extra fields or missing values), the data extraction logic may fail.
- **Assumption**: Dates and times are correctly formatted in the incident report.
- **Bug**: Handling of certain edge cases (e.g., locations or natures with unusual characters or formatting) may not be perfect and could lead to misclassification of data fields.

---

## Video Walkthrough
![video](video)
