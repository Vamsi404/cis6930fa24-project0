import unittest
import os
from main import download_pdf, extract_last_capital_onwards, extractincidents

class TestIncidentReportProcessing(unittest.TestCase):

    def test_download_pdf(self):
        # Assuming the URL is valid for testing
        test_url = "http://example.com/test.pdf"
        destination = "./tmp/test_incident_report.pdf"
        
        download_pdf(test_url, destination)
        self.assertTrue(os.path.exists(destination))
        
        # Clean up
        os.remove(destination)

    def test_extract_last_capital_onwards(self):
        test_string = "This is a sample Incident COP"
        result = extract_last_capital_onwards(test_string)
        self.assertEqual(result, "COP")

        test_string_no_match = "This is just text"
        result_no_match = extract_last_capital_onwards(test_string_no_match)
        self.assertEqual(result_no_match, "")

    def test_extractincidents(self):
        # Mocking the PDF reading functionality would be ideal
        # However, for a simplified case, we can test this as follows
        test_incidents = extractincidents()  # Assuming the PDF is read correctly
        self.assertIsInstance(test_incidents, list)
        # Check specific properties or content of the incidents
        # For this, a valid PDF file should be provided and processed

if __name__ == '__main__':
    unittest.main()
