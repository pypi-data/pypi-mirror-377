#!/usr/bin/env python
# Script            : Main script for model deployment
# Component         : GenAi model deployment
# Author            : Vinay Namani & Bijoy Kumar Roy
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import sys
import traceback
import logging
import logging.config
from pathlib import Path

# log_mode = "ERROR"
# Path("/opt/log_files").mkdir(parents=True, exist_ok=True)


def Logger(file_name):
    """Creates a logger for the application.

    Args:
        file_name (str): Name of the log file (without extension).

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(file_name)  # Use a specific logger instead of the root logger
    if logger.hasHandlers():
        # Prevent duplicate handlers
        return logger

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )

    # File handler
    file_handler = logging.FileHandler(filename="%s.log" % (file_name), mode="w")
    file_handler.setFormatter(formatter)

    # Stream handler for console output
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)

    return logger

def handle_exception():
    error_traceback = traceback.format_exc()
    traceback_lines = error_traceback.splitlines()
    error_traceback = traceback_lines[-1]
    error_message = "An error occurred. Traceback:\n" + error_traceback
    return str(error_message)