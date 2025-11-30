import logging
import sys
from typing import Optional
from .config import get_settings


_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """Get application logger (singleton)"""
    global _logger
    if _logger is None:
        settings = get_settings()
        _logger = logging.getLogger("microsaas_backend")
        _logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        _logger.addHandler(handler)
    
    return _logger

