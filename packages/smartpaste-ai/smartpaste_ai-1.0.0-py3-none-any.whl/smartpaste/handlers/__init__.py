"""
Content handlers for different clipboard data types.

This package contains specialized handlers for:
- URLs (title extraction, summarization, keyword generation)
- Numbers with units (automatic conversion)
- General text (language detection, summarization)
- Images (OCR text extraction)
- Code (language detection, syntax analysis)
- Email (parsing, validation, thread analysis)
- Math (expression evaluation, concept identification)
"""

from .url import URLHandler
from .number import NumberHandler
from .text import TextHandler
from .image import ImageHandler
from .code import CodeHandler
from .email import EmailHandler
from .math import MathHandler

__all__ = ["URLHandler", "NumberHandler", "TextHandler", "ImageHandler", 
           "CodeHandler", "EmailHandler", "MathHandler"]