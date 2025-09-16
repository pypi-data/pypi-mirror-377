import unittest
import unittest.mock as mock

from python_project_wizard.build_project.clean_main_content import clean_main_content
from python_project_wizard.project import Project


class BuildFilesTestSuite(unittest.TestCase):
    def test_one_removal(self):
        project = Project(name="merlin project")
        content = '''"""ppw: use_args-from args import get_argparser"""

def main():
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        expected_content = '''

def main():
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        new_content = clean_main_content(content, project)
        self.assertEqual(new_content, expected_content)

    def test_one_inclusion(self):
        project = Project(name="merlin project", use_args=True)
        content = '''"""ppw: use_args-from args import get_argparser"""

def main():
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        expected_content = '''from args import get_argparser

def main():
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        new_content = clean_main_content(content, project)
        self.assertEqual(new_content, expected_content)

    def test_one_multiline_inclusion(self):
        project = Project(name="merlin project", use_logging=True)
        content = '''"""ppw: use_logging-from log import enable_logging
import logging"""

def main():
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        expected_content = '''from log import enable_logging
import logging

def main():
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        new_content = clean_main_content(content, project)
        self.assertEqual(new_content, expected_content)

    def test_full_inclusion(self):
        project = Project(
            name="merlin project", use_logging=True, use_args=True, use_configs=True
        )
        content = '''"""ppw: use_args-from {project_name}.args import get_argparser"""
"""ppw: use_configs-from {project_name}.configs import load_configs"""
"""ppw: use_logging-from {project_name}.log import enable_logging
import logging"""

def main():
    """ppw: use_logging-# Enable logging
    enable_logging()
    logger = logging.getLogger(__name__)
    
    """
    """ppw: use_args-# Get the argument parser
    parser = get_argparser()
    args = parser.parse_args()
    
    """
    """ppw: use_configs-# Read Configs from JSON file
    configs = load_configs()
    """
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        expected_content = '''from merlin_project.args import get_argparser
from merlin_project.configs import load_configs
from merlin_project.log import enable_logging
import logging

def main():
    # Enable logging
    enable_logging()
    logger = logging.getLogger(__name__)
    
    
    # Get the argument parser
    parser = get_argparser()
    args = parser.parse_args()
    
    
    # Read Configs from JSON file
    configs = load_configs()
    
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        new_content = clean_main_content(content, project)
        self.assertEqual(new_content, expected_content)

    def test_full_exclusion(self):
        project = Project(name="merlin project")
        content = '''"""ppw: use_args-from {project_name}.args import get_argparser"""
"""ppw: use_configs-from {project_name}.configs import load_configs"""
"""ppw: use_logging-from {project_name}.log import enable_logging
import logging"""

def main():
    """ppw: use_logging-# Enable logging
    enable_logging()
    logger = logging.getLogger(__name__)
    
    """
    """ppw: use_args-# Get the argument parser
    parser = get_argparser()
    args = parser.parse_args()
    
    """
    """ppw: use_configs-# Read Configs from JSON file
    configs = load_configs()
    """
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        expected_content = '''



def main():
    
    
    
    """Cool stuff here!"""
    ...

if __name__ == "__main__":
    main()
'''
        new_content = clean_main_content(content, project)
        self.assertEqual(new_content, expected_content)
