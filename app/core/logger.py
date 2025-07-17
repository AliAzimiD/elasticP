"""
Tiny wrapper around stdlib logging so the rest of the code can import
`logger` directly.
"""

import logging
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("multilingual-doc-service")
