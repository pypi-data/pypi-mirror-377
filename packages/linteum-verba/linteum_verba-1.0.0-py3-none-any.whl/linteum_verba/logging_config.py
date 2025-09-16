"""
Linteum Verba - Rich Text Editor
Logging Configuration Module
"""
import os
import logging
import logging.handlers
from datetime import datetime

def configure_logging(log_level=logging.INFO, log_to_file=True):
    """
    Configure the logging system for the application
    
    Args:
        log_level: The logging level to use (default: INFO)
        log_to_file: Whether to log to a file (default: True)
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(logs_dir, f'linteum_verba_{timestamp}.log')
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Create loggers for main components
    loggers = {
        'editor': logging.getLogger('editor'),
        'canvas_renderer': logging.getLogger('canvas_renderer'),
        'text_manager': logging.getLogger('text_manager'),
        'syntax_highlighter': logging.getLogger('syntax_highlighter'),
    }
    
    # Set levels for component loggers
    for logger in loggers.values():
        logger.setLevel(log_level)
    
    logging.info("Logging system initialized")
    return loggers

# Default loggers (can be overridden by calling configure_logging)
LOGGERS = {
    'editor': logging.getLogger('editor'),
    'canvas_renderer': logging.getLogger('canvas_renderer'),
    'text_manager': logging.getLogger('text_manager'),
    'syntax_highlighter': logging.getLogger('syntax_highlighter'),
}
