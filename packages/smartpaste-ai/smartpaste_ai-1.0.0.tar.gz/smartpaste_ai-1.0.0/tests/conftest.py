"""
Pytest configuration and fixtures for SmartPaste tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "general": {
            "output_directory": "./test_output",
            "replace_clipboard": False,
            "check_interval": 0.1,
            "max_content_length": 1000
        },
        "features": {
            "url_handler": True,
            "number_handler": True,
            "text_handler": True,
            "image_handler": False
        },
        "url_handler": {
            "extract_title": True,
            "generate_summary": True,
            "extract_keywords": True,
            "max_keywords": 3,
            "request_timeout": 5
        },
        "number_handler": {
            "conversions": {
                "temperature": ["celsius", "fahrenheit", "kelvin"],
                "length": ["meter", "kilometer", "mile", "foot"],
                "weight": ["kilogram", "pound", "gram"],
                "volume": ["liter", "gallon", "milliliter"]
            }
        },
        "text_handler": {
            "detect_language": True,
            "generate_summary": True,
            "min_text_length": 50,
            "max_summary_length": 200
        }
    }


@pytest.fixture
def mock_clipboard():
    """Mock clipboard functionality."""
    with patch('pyperclip.paste') as mock_paste, \
         patch('pyperclip.copy') as mock_copy:
        
        clipboard_content = [""]
        
        def paste_side_effect():
            return clipboard_content[0]
        
        def copy_side_effect(content):
            clipboard_content[0] = content
        
        mock_paste.side_effect = paste_side_effect
        mock_copy.side_effect = copy_side_effect
        
        yield {
            'paste': mock_paste,
            'copy': mock_copy,
            'set_content': lambda content: clipboard_content.__setitem__(0, content),
            'get_content': lambda: clipboard_content[0]
        }


@pytest.fixture
def sample_html():
    """Sample HTML content for URL testing."""
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Sample Web Page</title>
            <meta property="og:title" content="Open Graph Title">
            <meta name="description" content="This is a sample web page for testing.">
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>This is the first paragraph with some content for testing.</p>
            <p>This is the second paragraph with additional information.</p>
            <p>The page contains multiple paragraphs to test content extraction.</p>
            <script>console.log('This should be removed');</script>
            <style>.hidden { display: none; }</style>
        </body>
    </html>
    """


@pytest.fixture
def sample_texts():
    """Sample text content for testing."""
    return {
        "english": "This is a sample English text that contains multiple sentences and provides enough content for language detection and summarization testing. The text discusses various topics and should be easily recognizable as English content. It includes common English words and grammatical structures that make it suitable for natural language processing tasks.",
        "code": "def process_data(input_data):\n    if not input_data:\n        return None\n    \n    results = []\n    for item in input_data:\n        processed_item = transform(item)\n        results.append(processed_item)\n    \n    return results",
        "short": "This text is too short for processing.",
        "numbers": "The temperature today is 25°C and the distance to the store is 2.5 km."
    }


@pytest.fixture
def mock_requests():
    """Mock requests library for URL testing."""
    with patch('requests.Session') as mock_session:
        mock_response = Mock()
        mock_response.text = """
        <html>
            <head><title>Test Page</title></head>
            <body><p>Test content for summarization and analysis.</p></body>
        </html>
        """
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.raise_for_status = Mock()
        
        mock_session.return_value.get.return_value = mock_response
        yield mock_session


@pytest.fixture
def mock_nlp_libraries():
    """Mock NLP libraries that might not be available."""
    with patch('smartpaste.utils.nlp.LANGDETECT_AVAILABLE', True), \
         patch('smartpaste.utils.nlp.ADVANCED_NLP_AVAILABLE', True), \
         patch('langdetect.detect') as mock_detect:
        
        mock_detect.return_value = 'en'
        yield {
            'detect': mock_detect
        }


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "slow: slow tests")
    config.addinivalue_line("markers", "network: tests requiring network access")
    config.addinivalue_line("markers", "optional: tests for optional dependencies")