"""
Tests for text handler functionality.
"""

import pytest
from smartpaste.handlers.text import TextHandler


class TestTextHandler:
    """Test cases for TextHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "detect_language": True,
            "generate_summary": True,
            "min_text_length": 50,
            "max_summary_length": 200,
            "supported_languages": ["en", "de", "fr", "es"]
        }
        self.handler = TextHandler(self.config)
    
    def test_process_valid_text(self):
        """Test processing valid text content."""
        content = """
        This is a sample text that is long enough to be processed by the text handler.
        It contains multiple sentences and should trigger language detection and summarization.
        The content is written in English and discusses various topics related to text processing.
        """
        
        result = self.handler.process(content)
        
        assert result is not None
        assert "original_content" in result
        assert "cleaned_content" in result
        assert "enriched_content" in result
        assert "analysis" in result
    
    def test_process_short_text(self):
        """Test processing text that is too short."""
        content = "Short text"
        result = self.handler.process(content)
        
        assert result is None
    
    def test_text_cleaning(self):
        """Test text cleaning functionality."""
        messy_text = "  This   is   messy   text  \\n\\n\\n  with   extra   spaces  \\r\\n  "
        cleaned = self.handler._clean_text(messy_text)
        
        assert "This is messy text" in cleaned
        assert "   " not in cleaned  # No triple spaces
        assert not cleaned.startswith(" ")  # No leading space
        assert not cleaned.endswith(" ")  # No trailing space
    
    def test_language_detection_english(self):
        """Test language detection for English text."""
        content = """
        This is a comprehensive English text that should be easily detectable by the language
        detection algorithm. It contains common English words and sentence structures that
        make it clearly identifiable as English content.
        """
        
        lang_info = self.handler._detect_language(content)
        
        # Note: Language detection might not be available in test environment
        if lang_info.get("language") != "unknown":
            assert lang_info["language"] == "en"
            assert lang_info["language_name"] == "English"
            assert lang_info["language_supported"] is True
    
    def test_language_detection_unknown(self):
        """Test language detection for unknown/unsupported language."""
        # Very short or ambiguous text
        content = "xyz abc def"
        
        lang_info = self.handler._detect_language(content)
        
        # Should handle gracefully
        assert "language" in lang_info
        assert "language_name" in lang_info
        assert "language_supported" in lang_info
    
    def test_summary_generation(self):
        """Test text summarization."""
        content = """
        Artificial intelligence has been a transformative technology in recent years.
        It has applications in many fields including healthcare, finance, and transportation.
        Machine learning algorithms can process vast amounts of data to identify patterns.
        These patterns help businesses make better decisions and improve their services.
        The future of AI looks promising with continued research and development.
        """
        
        summary_info = self.handler._generate_summary(content)
        
        assert "summary" in summary_info
        assert "summary_ratio" in summary_info
        
        if summary_info["summary"]:
            assert len(summary_info["summary"]) < len(content)
            assert summary_info["summary_ratio"] < 1.0
    
    def test_text_analysis(self):
        """Test text analysis functionality."""
        content = """
        This is a test document for analyzing text properties.
        It contains multiple sentences and various characteristics.
        The analysis should detect word count, sentence count, and other metrics.
        """
        
        analysis = self.handler._analyze_text(content)
        
        assert "word_count" in analysis
        assert "sentence_count" in analysis
        assert "character_count" in analysis
        assert "text_type" in analysis
        assert "readability_score" in analysis
        
        assert analysis["word_count"] > 0
        assert analysis["sentence_count"] > 0
        assert analysis["character_count"] > 0
    
    def test_text_type_classification(self):
        """Test text type classification."""
        # Test email detection
        email_text = "From: sender@example.com\\nTo: recipient@example.com\\nSubject: Test Email\\nDear John, this is a test email."
        assert self.handler._classify_text_type(email_text) == "email"
        
        # Test code detection
        code_text = "def function_name():\\n    if condition:\\n        return value"
        assert self.handler._classify_text_type(code_text) == "code"
        
        # Test list detection
        list_text = "• First item\\n• Second item\\n• Third item"
        assert self.handler._classify_text_type(list_text) == "list"
        
        # Test general text
        general_text = "This is just a regular paragraph of text without special formatting."
        assert self.handler._classify_text_type(general_text) == "general"
    
    def test_url_detection(self):
        """Test URL detection in text."""
        text_with_url = "Check out this website: https://example.com for more information."
        assert self.handler._contains_urls(text_with_url) is True
        
        text_without_url = "This text does not contain any web addresses."
        assert self.handler._contains_urls(text_without_url) is False
    
    def test_email_detection(self):
        """Test email address detection in text."""
        text_with_email = "Contact me at john.doe@example.com for more details."
        assert self.handler._contains_emails(text_with_email) is True
        
        text_without_email = "This text does not contain any email addresses."
        assert self.handler._contains_emails(text_without_email) is False
    
    def test_phone_detection(self):
        """Test phone number detection in text."""
        text_with_phone = "Call me at 123-456-7890 or (555) 123-4567."
        assert self.handler._contains_phone_numbers(text_with_phone) is True
        
        text_without_phone = "This text does not contain any phone numbers."
        assert self.handler._contains_phone_numbers(text_without_phone) is False
    
    def test_readability_score(self):
        """Test readability score calculation."""
        # Simple text
        simple_text = "This is a simple text. It has short sentences. Easy to read."
        score = self.handler._calculate_readability_score(simple_text)
        assert score is not None
        assert 0 <= score <= 100
        
        # Complex text
        complex_text = "This is an extraordinarily complicated and convoluted sentence that demonstrates the utilization of unnecessarily sophisticated vocabulary and excessively lengthy sentence structures."
        complex_score = self.handler._calculate_readability_score(complex_text)
        assert complex_score is not None
        
        # Simple text should generally have higher readability
        if score and complex_score:
            assert score >= complex_score
    
    def test_enriched_content_generation(self):
        """Test enriched content generation."""
        content = """
        This is a sample text for testing enriched content generation.
        The handler should create enhanced content with language detection and summary.
        """
        
        result = self.handler.process(content)
        
        if result:
            enriched = result["enriched_content"]
            assert content in enriched  # Original content should be included
            
            # If summary was generated, it should be in enriched content
            if result.get("summary"):
                assert "TL;DR:" in enriched


class TestTextHandlerEdgeCases:
    """Test edge cases for TextHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = TextHandler()
    
    def test_empty_text(self):
        """Test processing empty text."""
        result = self.handler.process("")
        assert result is None
    
    def test_whitespace_only_text(self):
        """Test processing text with only whitespace."""
        result = self.handler.process("   \\n\\t   ")
        assert result is None
    
    def test_minimum_length_boundary(self):
        """Test text at minimum length boundary."""
        # Text exactly at minimum length
        min_text = "a" * self.handler.min_text_length
        result = self.handler.process(min_text)
        assert result is not None
        
        # Text just below minimum length
        short_text = "a" * (self.handler.min_text_length - 1)
        result = self.handler.process(short_text)
        assert result is None
    
    def test_very_long_text(self):
        """Test processing very long text."""
        long_text = "This is a sentence. " * 1000  # Very long text
        result = self.handler.process(long_text)
        
        assert result is not None
        # Should handle long text gracefully
        assert len(result["cleaned_content"]) > 0
    
    def test_special_characters(self):
        """Test processing text with special characters."""
        special_text = """
        This text contains special characters: äöü, ñ, 中文, العربية, русский.
        It should be processed correctly despite the unicode characters.
        The handler should maintain the integrity of the special characters.
        """
        
        result = self.handler.process(special_text)
        
        assert result is not None
        assert "äöü" in result["cleaned_content"]
        assert "中文" in result["cleaned_content"]
    
    def test_handler_initialization_default_config(self):
        """Test handler initialization with default configuration."""
        handler = TextHandler()
        
        assert handler.detect_language is True
        assert handler.generate_summary is True
        assert handler.min_text_length == 50
        assert handler.max_summary_length == 200
    
    def test_handler_initialization_custom_config(self):
        """Test handler initialization with custom configuration."""
        config = {
            "detect_language": False,
            "generate_summary": False,
            "min_text_length": 100,
            "max_summary_length": 300,
        }
        handler = TextHandler(config)
        
        assert handler.detect_language is False
        assert handler.generate_summary is False
        assert handler.min_text_length == 100
        assert handler.max_summary_length == 300