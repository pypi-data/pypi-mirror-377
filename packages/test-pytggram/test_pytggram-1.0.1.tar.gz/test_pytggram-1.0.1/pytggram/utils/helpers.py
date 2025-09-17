import json
import logging
from typing import Any, Dict

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Set up a logger with a standard format"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def parse_json(data: str) -> Dict[str, Any]:
    """Parse JSON string and return dictionary"""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {}
