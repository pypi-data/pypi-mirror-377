"""
Text content handler for SmartPaste.

This module handles general text content by detecting language,
generating summaries, and providing text analysis.
"""

import logging
from typing import Dict, Any, Optional

from ..utils.nlp import NLPUtils


class TextHandler:
    """Handler for general text content processing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize text handler.
        
        Args:
            config: Configuration dictionary for text handling
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration defaults
        self.detect_language = self.config.get("detect_language", True)
        self.generate_summary = self.config.get("generate_summary", True)
        self.min_text_length = self.config.get("min_text_length", 50)
        self.max_summary_length = self.config.get("max_summary_length", 200)
        self.supported_languages = self.config.get("supported_languages", [
            "en", "de", "fr", "es", "it"
        ])
    
    def process(self, content: str) -> Optional[Dict[str, Any]]:
        """Process text content.
        
        Args:
            content: Text content from clipboard
            
        Returns:
            Dictionary with processed text information or None if processing fails
        """
        # Clean the content
        cleaned_content = self._clean_text(content)
        
        # Check minimum length
        if len(cleaned_content) < self.min_text_length:
            return None
        
        result = {
            "original_content": content,
            "cleaned_content": cleaned_content,
            "enriched_content": content
        }
        
        # Detect language
        if self.detect_language:
            language_info = self._detect_language(cleaned_content)
            result.update(language_info)
        
        # Generate summary
        if self.generate_summary:
            summary_info = self._generate_summary(cleaned_content)
            result.update(summary_info)
            
            # Update enriched content with summary
            if summary_info.get("summary"):
                language_part = ""
                if language_info.get("language_name"):
                    language_part = f"[{language_info['language_name']}] "
                
                result["enriched_content"] = f"{language_part}TL;DR: {summary_info['summary']}\\n\\n{content}"
        
        # Add text analysis
        analysis = self._analyze_text(cleaned_content)
        result["analysis"] = analysis
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text content
        """
        # Remove excessive whitespace
        import re
        
        # Normalize line endings
        text = re.sub(r'\\r\\n|\\r', '\\n', text)
        
        # Remove excessive blank lines
        text = re.sub(r'\\n\\s*\\n\\s*\\n+', '\\n\\n', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\\n')]
        text = '\\n'.join(lines)
        
        # Remove excessive spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def _detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with language information
        """
        result = {}
        
        try:
            language_code = NLPUtils.detect_language(text)
            
            if language_code:
                result["language"] = language_code
                result["language_name"] = NLPUtils.get_language_name(language_code)
                
                # Check if language is supported
                is_supported = language_code in self.supported_languages
                result["language_supported"] = is_supported
                
                if not is_supported:
                    self.logger.debug(f"Detected unsupported language: {language_code}")
            else:
                result["language"] = "unknown"
                result["language_name"] = "Unknown"
                result["language_supported"] = False
                
        except Exception as e:
            self.logger.debug(f"Language detection failed: {e}")
            result["language"] = "unknown"
            result["language_name"] = "Unknown"
            result["language_supported"] = False
        
        return result
    
    def _generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate a summary of the text.
        
        Args:
            text: Text to summarize
            
        Returns:
            Dictionary with summary information
        """
        result = {}
        
        try:
            # Generate summary using NLP utils
            summary = NLPUtils.summarize_text_simple(text, max_sentences=2)
            
            if summary and summary != text:
                # Truncate summary if too long
                if len(summary) > self.max_summary_length:
                    # Find a good breaking point
                    truncated = summary[:self.max_summary_length]
                    last_period = truncated.rfind('.')
                    last_space = truncated.rfind(' ')
                    
                    if last_period > self.max_summary_length * 0.8:
                        summary = truncated[:last_period + 1]
                    elif last_space > self.max_summary_length * 0.8:
                        summary = truncated[:last_space] + "..."
                    else:
                        summary = truncated + "..."
                
                result["summary"] = summary
                result["summary_ratio"] = len(summary) / len(text)
            else:
                result["summary"] = None
                result["summary_ratio"] = 1.0
                
        except Exception as e:
            self.logger.debug(f"Summary generation failed: {e}")
            result["summary"] = None
            result["summary_ratio"] = 1.0
        
        return result
    
    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text properties.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with text analysis
        """
        try:
            # Get basic statistics
            stats = NLPUtils.calculate_text_stats(text)
            
            # Add additional analysis
            analysis = {
                **stats,
                "readability_score": self._calculate_readability_score(text),
                "text_type": self._classify_text_type(text),
                "contains_urls": self._contains_urls(text),
                "contains_emails": self._contains_emails(text),
                "contains_phone_numbers": self._contains_phone_numbers(text),
            }
            
            return analysis
            
        except Exception as e:
            self.logger.debug(f"Text analysis failed: {e}")
            return {"error": "Analysis failed"}
    
    def _calculate_readability_score(self, text: str) -> Optional[float]:
        """Calculate a simple readability score.
        
        Args:
            text: Text to analyze
            
        Returns:
            Readability score (0-100, higher is more readable)
        """
        try:
            sentences = NLPUtils.extract_sentences(text)
            words = text.split()
            
            if not sentences or not words:
                return None
            
            # Simple readability score based on average sentence length and word length
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # Flesch-like scoring (simplified)
            score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length / 5)
            
            # Normalize to 0-100
            score = max(0, min(100, score))
            
            return round(score, 1)
            
        except Exception:
            return None
    
    def _classify_text_type(self, text: str) -> str:
        """Classify the type of text content.
        
        Args:
            text: Text to classify
            
        Returns:
            Text type classification
        """
        import re
        
        text_lower = text.lower()
        
        # Email patterns
        if re.search(r'from:|to:|subject:|dear\s+\w+', text_lower):
            return "email"
        
        # Code patterns
        if re.search(r'\b(def|class|import|function|var|const|if|else|for|while)\b', text_lower):
            return "code"
        
        # List patterns
        if re.search(r'^\s*[-*•]\s+|^\s*\d+\.\s+', text, re.MULTILINE):
            return "list"
        
        # News/article patterns
        if re.search(r'\b(today|yesterday|reported|according to|sources)\b', text_lower):
            return "news"
        
        # Question patterns
        if text.count('?') > len(text) / 100:  # More than 1% question marks
            return "questions"
        
        # Default
        return "general"
    
    def _contains_urls(self, text: str) -> bool:
        """Check if text contains URLs.
        
        Args:
            text: Text to check
            
        Returns:
            True if URLs are found
        """
        import re
        url_pattern = r'https?://[^\\s]+|www\\.[^\\s]+|[^\\s]+\\.[a-z]{2,}(?:/[^\\s]*)?'
        return bool(re.search(url_pattern, text, re.IGNORECASE))
    
    def _contains_emails(self, text: str) -> bool:
        """Check if text contains email addresses.
        
        Args:
            text: Text to check
            
        Returns:
            True if email addresses are found
        """
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return bool(re.search(email_pattern, text))
    
    def _contains_phone_numbers(self, text: str) -> bool:
        """Check if text contains phone numbers.
        
        Args:
            text: Text to check
            
        Returns:
            True if phone numbers are found
        """
        import re
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 or 123.456.7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (123) 456-7890
            r'\+\d{1,3}[-.]?\d{3,14}',            # International format
        ]
        
        for pattern in phone_patterns:
            if re.search(pattern, text):
                return True
        
        return False