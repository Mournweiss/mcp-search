"""
Structured logging configuration for MCP Search Server.

Provides structured logging with JSON format and correlation IDs.
"""

import logging
import json
from typing import Dict, Any
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Outputs log messages in JSON format with standardized fields.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the JSON formatter."""
        super().__init__(*args, **kwargs)
        
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.
        
        Args:
            record (logging.LogRecord): The log record to format
            
        Returns:
            str: JSON formatted log message
        """
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in ("name", "msg", "args", "levelname", "levelno", 
                          "pathname", "filename", "module", "lineno", "funcName",
                          "thread", "threadName", "processName", "process",
                          "getMessage", "exc_info", "exc_text", "stack_info"):
                log_entry[key] = value
                
        return json.dumps(log_entry)


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup and configure a logger with structured formatting.
    
    Args:
        name (str): Name of the logger
        level (str): Logging level
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid adding multiple handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
    return logger