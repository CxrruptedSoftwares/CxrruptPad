#!/usr/bin/env python3
from src.main import main
from src.utils.logger import logger, get_log_directory

if __name__ == "__main__":
    logger.info(f"CxrruptPad starting - logs available at: {get_log_directory()}/latest.log")
    main()
