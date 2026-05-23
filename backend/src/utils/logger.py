"""
Logging configuration module
Provides structured logging for the application
"""
import logging
import logging.handlers
import sys
import io
from pathlib import Path
from config import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger instance
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)

    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    # Ensure file handler writes UTF-8
    try:
        file_handler.setLevel(settings.log_level)
        file_handler.encoding = 'utf-8'
    except Exception:
        # Older handlers may not support setting encoding attribute directly
        pass
    file_handler.setLevel(settings.log_level)
    file_handler.setFormatter(formatter)

    # Console handler (wrap stdout.buffer with a UTF-8 TextIOWrapper when possible)
    console_stream = None
    try:
        # If stdout has a buffer attribute (usual in real terminals), wrap it
        if hasattr(sys.stdout, 'buffer'):
            console_stream = io.TextIOWrapper(
                sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True
            )
        else:
            # Fallback: try to reconfigure sys.stdout encoding where supported
            if hasattr(sys.stdout, 'reconfigure'):
                try:
                    sys.stdout.reconfigure(encoding='utf-8')
                except Exception:
                    pass
            console_stream = sys.stdout
    except Exception:
        console_stream = sys.stdout

    console_handler = logging.StreamHandler(console_stream)
    console_handler.setLevel(settings.log_level)
    console_handler.setFormatter(formatter)

    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Create module logger
logger = setup_logger(__name__)
