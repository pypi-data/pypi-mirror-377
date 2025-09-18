"""
Logging utilities for DistinaNet training and evaluation.
"""
import logging
import sys
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels and logger names."""
    
    # ANSI color codes for log levels
    LEVEL_COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    
    # Dynamic color assignment for logger components
    COMPONENT_COLORS = [
        '\033[94m',   # Bright Blue
        '\033[97m',   # Bright White
        '\033[96m',   # Bright Cyan
        '\033[93m',   # Bright Yellow
        '\033[95m',   # Bright Magenta
        '\033[91m',   # Bright Red
        '\033[92m',   # Bright Green
        '\033[90m',   # Bright Black (Gray)
        '\033[34m',   # Blue
        '\033[35m',   # Magenta
        '\033[32m',   # Green
        '\033[36m',   # Cyan
        '\033[33m',   # Yellow
        '\033[31m',   # Red
        '\033[37m',   # White
        '\033[30m',   # Black
    ]
    
    RESET = '\033[0m'  # Reset color
    
    # Class-level cache for assigned colors
    _color_index = 0
    _color_assignments = {}
    
    def _get_name_color(self, name: str) -> str:
        """Get a color for a logger name using dynamic assignment."""
        # For new components, assign a color consistently
        if name not in self._color_assignments:
            color_index = self._color_index % len(self.COMPONENT_COLORS)
            self._color_assignments[name] = self.COMPONENT_COLORS[color_index]
            ColoredFormatter._color_index += 1
        
        return self._color_assignments[name]
    
    def format(self, record):
        # Get the original formatted message
        log_message = super().format(record)
        
        # Add color to the log level
        level_name = record.levelname
        if level_name in self.LEVEL_COLORS:
            colored_level = f"{self.LEVEL_COLORS[level_name]}{level_name}{self.RESET}"
            # Replace the level name in the message with the colored version
            log_message = log_message.replace(level_name, colored_level, 1)
        
        # Add color to the logger name
        logger_name = record.name
        name_color = self._get_name_color(logger_name)
        colored_name = f"{name_color}{logger_name}{self.RESET}"
        # Replace the logger name in the message with the colored version
        log_message = log_message.replace(f" - {logger_name} - ", f" - {colored_name} - ", 1)
        
        # Add color to filename:lineno for better visibility
        filename_lineno = f"{record.filename}:{record.lineno}"
        colored_filename = f"\033[90m{filename_lineno}\033[0m"  # Gray color for file:line
        log_message = log_message.replace(f" - {filename_lineno} - ", f" - {colored_filename} - ", 1)
        
        return log_message

def setup_logger(
    name: str = "distinanet",
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    Set up logger for DistinaNet with consistent formatting and optional colors.
    
    Args:
        name: Logger name (can be any string)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to write logs to
        use_colors: Whether to use colored output for console (default: True)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters with file and line info, shorter format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    date_format = '%m/%d %H:%M:%S'  # Time format
    
    # Console handler with colored formatter
    console_handler = logging.StreamHandler(sys.stdout)
    if use_colors and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        # Use colored formatter for terminal output
        console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        # Use plain formatter for non-terminal output (e.g., redirected to file)
        console_formatter = logging.Formatter(log_format, datefmt=date_format)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional) - always use plain formatter for files
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "distinanet") -> logging.Logger:
    """Get existing logger or create default one."""
    return logging.getLogger(name)
