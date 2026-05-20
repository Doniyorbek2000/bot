"""Logging configuration."""
import logging
import sys
from app.utils.config import settings


def setup_logger(name: str = "hudud_bot") -> logging.Logger:
    """
    Setup logger with console output.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with simple formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Force flush
    handler.flush = lambda: sys.stdout.flush()
    
    return logger


# Global logger instance
logger = setup_logger()
logger.info("Logger initialized")
