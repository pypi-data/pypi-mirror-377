"""
Tests for URL handler functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from smartpaste.handlers.url import URLHandler


class TestURLHandler:
    """Test cases for URLHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "extract_title": True,
            "generate_summary": True,
            "extract_keywords": True,
            "max_keywords": 3,
            "request_timeout": 5,
        }
        self.handler = URLHandler(self.config)
    
    def test_clean_url_valid_https(self):
        """Test cleaning valid HTTPS URLs."""
        url = "https://example.com/test"
        result = self.handler._clean_url(url)
        assert result == url
    
    def test_clean_url_valid_http(self):
        """Test cleaning valid HTTP URLs."""
        url = "http://example.com/test"
        result = self.handler._clean_url(url)
        assert result == url
    
    def test_clean_url_www_prefix(self):
        """Test cleaning URLs with www prefix."""
        url = "www.example.com"
        result = self.handler._clean_url(url)
        assert result == "https://www.example.com"
    
    def test_clean_url_no_protocol(self):
        """Test cleaning URLs without protocol."""
        url = "example.com"
        result = self.handler._clean_url(url)
        assert result == "https://example.com"
    
    def test_clean_url_invalid(self):
        """Test cleaning invalid URLs."""
        invalid_urls = ["not a url", "just text", ""]
        for url in invalid_urls:
            result = self.handler._clean_url(url)
            assert result is None
    
    def test_clean_title(self):
        """Test title cleaning functionality."""
        # Test basic cleaning
        title = "  Test Title  "
        result = self.handler._clean_title(title)
        assert result == "Test Title"
        
        # Test suffix removal
        title = "Test Title | Some Site"
        result = self.handler._clean_title(title)
        assert result == "Test Title"
        
        title = "Test Title - Some Site"
        result = self.handler._clean_title(title)
        assert result == "Test Title"
        
        # Test long title truncation
        long_title = "A" * 150
        result = self.handler._clean_title(long_title)
        assert len(result) <= 100
        assert result.endswith("...")
    
    @patch('smartpaste.handlers.url.WEB_SCRAPING_AVAILABLE', True)
    @patch('smartpaste.handlers.url.requests')
    @patch('smartpaste.handlers.url.Document')
    @patch('smartpaste.handlers.url.BeautifulSoup')
    def test_process_success(self, mock_soup, mock_document, mock_requests):
        """Test successful URL processing."""
        # Mock HTML content
        mock_html = """
        <html>
            <head>
                <title>Test Page Title</title>
                <meta property="og:title" content="OG Title">
            </head>
            <body>
                <h1>Main Heading</h1>
                <p>This is a test paragraph with some content for summarization.</p>
                <p>Another paragraph with more content to make it substantial.</p>
            </body>
        </html>
        """
        
        # Mock response
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.raise_for_status = Mock()
        mock_requests.Session().get.return_value = mock_response
        
        # Mock readability
        mock_doc = Mock()
        mock_doc.summary.return_value = "<p>This is a test paragraph with some content for summarization. Another paragraph with more content to make it substantial.</p>"
        mock_document.return_value = mock_doc

        # Mock BeautifulSoup for title extraction and text extraction
        mock_title_tag = Mock()
        mock_title_tag.get_text.return_value = "Test Page Title"
        mock_title_tag.name = "title"

        # Create a mock element that can be decomposed
        mock_elements = []
        mock_element = Mock()
        mock_element.decompose = Mock()
        mock_elements.append(mock_element)

        mock_soup_instance = Mock()
        mock_soup_instance.find.return_value = mock_title_tag
        # Return text for both get_text calls
        mock_soup_instance.get_text.return_value = "This is a test paragraph with some content for summarization. Another paragraph with more content to make it substantial."
        # Mock elements for decompose() - return empty list
        def mock_call(*args):
            return []
        mock_soup_instance.__call__ = mock_call
        mock_soup.return_value = mock_soup_instance        # Test processing
        result = self.handler.process("https://example.com")

        assert result is not None
        assert result["url"] == "https://example.com"
        assert "title" in result
        assert "enriched_content" in result
        assert "enriched_content" in result
    
    @patch('smartpaste.handlers.url.WEB_SCRAPING_AVAILABLE', False)
    def test_process_no_libraries(self):
        """Test processing when web scraping libraries are not available."""
        handler = URLHandler()
        result = handler.process("https://example.com")
        
        assert result is not None
        assert result["url"] == "https://example.com"
        assert "title extraction unavailable" in result["title"]
        assert "Install requests" in result["summary"]
    
    @patch('smartpaste.handlers.url.WEB_SCRAPING_AVAILABLE', True)
    def test_process_invalid_url(self):
        """Test processing invalid URLs."""
        result = self.handler.process("not a url")
        assert result is None
    
    @patch('smartpaste.handlers.url.WEB_SCRAPING_AVAILABLE', True)
    @patch('smartpaste.handlers.url.requests')
    def test_process_request_failure(self, mock_requests):
        """Test processing when HTTP request fails."""
        # Mock failed request
        mock_requests.Session().get.side_effect = Exception("Connection failed")
        
        result = self.handler.process("https://example.com")
        
        assert result is not None
        assert "title" in result


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <html>
        <head>
            <title>Sample Page Title</title>
            <meta property="og:title" content="OG Sample Title">
            <meta name="twitter:title" content="Twitter Sample Title">
        </head>
        <body>
            <h1>Main Content Heading</h1>
            <p>This is the first paragraph of content.</p>
            <p>This is the second paragraph with more details.</p>
            <script>console.log('should be removed');</script>
            <style>.hidden { display: none; }</style>
        </body>
    </html>
    """


class TestURLHandlerIntegration:
    """Integration tests for URL handler."""
    
    def test_handler_initialization_default_config(self):
        """Test handler initialization with default configuration."""
        handler = URLHandler()
        
        assert handler.extract_title is True
        assert handler.generate_summary is True
        assert handler.extract_keywords is True
        assert handler.max_keywords == 3
        assert handler.request_timeout == 10
    
    def test_handler_initialization_custom_config(self):
        """Test handler initialization with custom configuration."""
        config = {
            "extract_title": False,
            "generate_summary": False,
            "max_keywords": 5,
            "request_timeout": 15,
        }
        handler = URLHandler(config)
        
        assert handler.extract_title is False
        assert handler.generate_summary is False
        assert handler.max_keywords == 5
        assert handler.request_timeout == 15