import os
import unittest
import unittest.mock as mock

from python_project_wizard.file import File, Destination


class FileTestSuite(unittest.TestCase):
    def test_constructor(self):
        test_file = File(
            filename="main.py", content="...", destination=Destination.SOURCE
        )
        self.assertIsInstance(test_file, File)
        self.assertIsInstance(test_file.filename, str)
        self.assertIsInstance(test_file.content, str)
        self.assertIsInstance(test_file.destination, Destination)

    def test_defaults(self):
        test_file = File()
        self.assertIsInstance(test_file, File)
        self.assertEqual(test_file.filename, File.INVALID_FILENAME)
        self.assertEqual(test_file.content, "")
        self.assertEqual(test_file.destination, Destination.INVALID)

    def test_is_valid(self):
        invalid_files = [
            File(filename="main.py"),
            File(
                filename=File.INVALID_FILENAME, content="", destination=Destination.MAIN
            ),
            File(content="# Main file"),
            File(destination=Destination.MAIN),
            File(filename="main.py", content="# Main"),
            File(
                filename="main.py",
                content="# Main file",
                destination=Destination.INVALID,
            ),
        ]
        valid_files = [
            File(
                filename="main.py",
                content="# Main File",
                destination=Destination.SOURCE,
            ),
            File(filename="config.json", content="{}", destination=Destination.MAIN),
            File(filename="launch.json", content="{}", destination=Destination.VS_CODE),
            File(filename="test_example.py", content="", destination=Destination.TEST),
        ]
        for invalid_file in invalid_files:
            self.assertFalse(invalid_file.is_valid())
        for valid_file in valid_files:
            self.assertTrue(valid_file.is_valid())
