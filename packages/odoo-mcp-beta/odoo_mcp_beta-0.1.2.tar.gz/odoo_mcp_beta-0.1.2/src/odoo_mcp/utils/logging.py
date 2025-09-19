"""
Logging utilities for the Odoo MCP server
"""

import os
import logging
import datetime
from pathlib import Path


def setup_logging(log_dir=None, log_level=None):
    """
    Set up logging to both console and file
    
    Args:
        log_dir: Directory for log files (default: logs dir in project root)
        log_level: Logging level (default: DEBUG)
        
    Returns:
        Logger instance configured with console and file handlers
    """
    # Determine log directory
    if log_dir is None:
        # Use project root/logs by default
        project_root = Path(__file__).parent.parent.parent.parent.absolute()
        log_dir = project_root / "logs"
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate timestamped log filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"mcp_server_{timestamp}.log")
    
    # Set log level
    if log_level is None:
        log_level = logging.DEBUG
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates on restart
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with INFO level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler with DEBUG level (more detailed)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Format for both handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Log the log file location
    logger.info(f"Logging to file: {log_file}")
    
    return logger
