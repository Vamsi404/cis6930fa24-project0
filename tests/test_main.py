import unittest
import os
import project0.main as testMain

class TestIncidentReportProcessing(unittest.TestCase):

    def test_incidentPdf_exists(self):
        file_path = './tmp/Incident_Report.pdf'
        self.assertTrue(os.path.exists(file_path), f"File '{file_path}' does not exist.")

    def test_extract_last_capital_onwards(self):
        test_string = "This is a sample Incident COP"
        result = testMain.get_last_capital_segment(test_string)
        self.assertEqual(result, "COP")

        test_string_no_match = "This is just text"
        result_no_match = testMain.get_last_capital_segment(test_string_no_match)
        self.assertEqual(result_no_match, "")

    def test_extractincidents(self):
        # Mocking the PDF reading functionality would be ideal
        # However, for a simplified case, we can test this as follows
        test_incidents = testMain.extract_incidents()  # Assuming the PDF is read correctly
        self.assertIsInstance(test_incidents, list)
        # Check specific properties or content of the incidents
        # For this, a valid PDF file should be provided and processed

if __name__ == '__main__':
    unittest.main()
