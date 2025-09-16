"""ppw: use_args-from {project_name}.args import get_argparser
""""""ppw: use_configs-from {project_name}.configs import load_configs
""""""ppw: use_logging-from {project_name}.log import enable_logging
import logging
"""


def main():
    """ppw: use_logging-# Enable logging
    enable_logging()
    logger = logging.getLogger(__name__)
    
    """"""ppw: use_args-# Get the argument parser
    parser = get_argparser()
    args = parser.parse_args()
    
    """"""ppw: use_configs-# Read Configs from JSON file
    configs = load_configs()

    """
    """Cool stuff here!"""
    ...


if __name__ == "__main__":
    main()
