"""
Image OCR handler for SmartPaste.

This module handles image content by extracting text using OCR (Optical Character Recognition).
Requires pytesseract and Pillow to be installed.
"""

import logging
from typing import Dict, Any, Optional
import base64
import io

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class ImageHandler:
    """Handler for image OCR processing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize image handler.
        
        Args:
            config: Configuration dictionary for image handling
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        if not OCR_AVAILABLE:
            self.logger.warning("OCR libraries not available (pytesseract, Pillow)")
            return
        
        # Configuration defaults
        self.ocr_language = self.config.get("ocr_language", "eng")
        self.min_confidence = self.config.get("min_confidence", 60)
        self.post_process = self.config.get("post_process", True)
        
        # Test tesseract installation
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            self.logger.error(f"Tesseract not properly installed: {e}")
            # Note: Cannot modify global OCR_AVAILABLE from instance method
            # This will be handled gracefully in process() method
    
    def process(self, content: str) -> Optional[Dict[str, Any]]:
        """Process image content using OCR.
        
        Args:
            content: Image data (base64 encoded or file path)
            
        Returns:
            Dictionary with OCR results or None if processing fails
        """
        if not OCR_AVAILABLE:
            return {
                "original_content": content[:100] + "..." if len(content) > 100 else content,
                "extracted_text": "",
                "confidence": 0,
                "error": "OCR libraries not available. Install pytesseract and Pillow.",
                "enriched_content": "Image (OCR unavailable)"
            }
        
        try:
            # Load image
            image = self._load_image(content)
            if image is None:
                return None
            
            # Perform OCR
            ocr_result = self._extract_text_from_image(image)
            
            if not ocr_result:
                return {
                    "original_content": content[:100] + "..." if len(content) > 100 else content,
                    "extracted_text": "",
                    "confidence": 0,
                    "error": "No text detected in image",
                    "enriched_content": "Image (no text detected)"
                }
            
            extracted_text = ocr_result.get("text", "")
            confidence = ocr_result.get("confidence", 0)
            
            # Post-process text if enabled
            if self.post_process and extracted_text:
                extracted_text = self._post_process_text(extracted_text)
            
            # Check minimum confidence
            if confidence < self.min_confidence:
                self.logger.debug(f"OCR confidence {confidence}% below threshold {self.min_confidence}%")
            
            # Create enriched content
            enriched_content = f"Image Text: {extracted_text}" if extracted_text else "Image (no readable text)"
            
            return {
                "original_content": content[:100] + "..." if len(content) > 100 else content,
                "extracted_text": extracted_text,
                "confidence": confidence,
                "language": self.ocr_language,
                "enriched_content": enriched_content
            }
            
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
            return {
                "original_content": content[:100] + "..." if len(content) > 100 else content,
                "extracted_text": "",
                "confidence": 0,
                "error": f"OCR processing failed: {str(e)}",
                "enriched_content": "Image (processing failed)"
            }
    
    def _load_image(self, content: str) -> Optional[Any]:
        """Load image from various sources.
        
        Args:
            content: Image content (base64, file path, or binary data)
            
        Returns:
            PIL Image object or None if loading fails
        """
        if not OCR_AVAILABLE:
            return None
            
        try:
            # Try base64 data URL format
            if content.startswith("data:image/"):
                header, encoded = content.split(",", 1)
                image_data = base64.b64decode(encoded)
                return Image.open(io.BytesIO(image_data))
            
            # Try direct base64
            elif self._is_base64(content):
                image_data = base64.b64decode(content)
                return Image.open(io.BytesIO(image_data))
            
            # Try file path
            elif content.startswith(("/", "\\", "C:", "D:")) or "." in content:
                try:
                    return Image.open(content)
                except FileNotFoundError:
                    pass
            
            # Try binary data
            else:
                return Image.open(io.BytesIO(content.encode('latin-1')))
                
        except Exception as e:
            self.logger.debug(f"Failed to load image: {e}")
            return None
    
    def _is_base64(self, content: str) -> bool:
        """Check if content is base64 encoded.
        
        Args:
            content: Content to check
            
        Returns:
            True if content appears to be base64
        """
        try:
            # Base64 should be divisible by 4 and contain only valid chars
            if len(content) % 4 != 0:
                return False
            
            base64.b64decode(content[:100])  # Test decode a small portion
            return True
        except Exception:
            return False
    
    def _extract_text_from_image(self, image: Any) -> Optional[Dict[str, Any]]:
        """Extract text from image using OCR.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with OCR results
        """
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get OCR data with confidence scores
            ocr_data = pytesseract.image_to_data(
                image,
                lang=self.ocr_language,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text and calculate average confidence
            words = []
            confidences = []
            
            for i, conf in enumerate(ocr_data['conf']):
                if int(conf) > 0:  # Valid detection
                    text = ocr_data['text'][i].strip()
                    if text:
                        words.append(text)
                        confidences.append(int(conf))
            
            if not words:
                return None
            
            # Combine words and calculate average confidence
            extracted_text = ' '.join(words)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "text": extracted_text,
                "confidence": round(avg_confidence, 1),
                "word_count": len(words)
            }
            
        except Exception as e:
            self.logger.debug(f"OCR extraction failed: {e}")
            return None
    
    def _post_process_text(self, text: str) -> str:
        """Post-process extracted text to improve quality.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\\s+', ' ', text)
        
        # Fix common OCR errors
        ocr_fixes = {
            r'\\b0\\b': 'O',  # Zero to O
            r'\\bl\\b': 'I',  # lowercase l to I
            r'\\b5\\b': 'S',  # 5 to S in some contexts
            r'\\b8\\b': 'B',  # 8 to B in some contexts
        }
        
        for pattern, replacement in ocr_fixes.items():
            text = re.sub(pattern, replacement, text)
        
        # Remove isolated single characters (likely noise)
        text = re.sub(r'\\b[a-z]\\b', '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        text = re.sub(r'\\s+', ' ', text).strip()
        
        return text