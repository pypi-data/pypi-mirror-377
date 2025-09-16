import os
import unittest
import unittest.mock as mock

from python_project_wizard.file_content_store.file_content_store import FileContentStore
from python_project_wizard.file_content_store.folder_store import FolderStore


class FolderTestSuite(unittest.TestCase):
    def test_default_constructor(self):
        folder_store = FolderStore()
        self.assertIsInstance(folder_store, FileContentStore)

    def test_main_folder_store(self):
        folder_store = FolderStore()
        files = folder_store.get_file_content()
        self.assertIn("args.py", files.keys())
        self.assertIn("configs.json", files.keys())
        self.assertIn("configs.py", files.keys())
        self.assertIn("log.py", files.keys())
        self.assertIn("logging.conf", files.keys())
        self.assertIn("main.py", files.keys())

    def test_get_files_return_type(self):
        self.assertIsInstance(FolderStore().get_file_content(), dict)
