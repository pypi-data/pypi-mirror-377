"""
cbases - A library for number base conversion including Roman numerals.
"""

from .core import convert, EquBase
import logging

__version__ = "1.0.0"
__all__ = ['convert', 'EquBase']
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Thanks for using this module! For more informations about this module or to report an issue, go to https://github.com/MagnusGabinus/cbases")