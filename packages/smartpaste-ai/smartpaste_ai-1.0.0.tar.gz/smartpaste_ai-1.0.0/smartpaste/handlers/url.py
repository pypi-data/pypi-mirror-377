"""
URL content handler for SmartPaste.

This module handles URL clipboard content by extracting titles,
generating summaries, and extracting keywords from web pages.
"""

import logging
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin
import time

try:
    import requests
    from readability import Document
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False

from ..utils.nlp import NLPUtils


class URLHandler:
    """Handler for URL content processing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize URL handler.
        
        Args:
            config: Configuration dictionary for URL handling
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration defaults
        self.extract_title = self.config.get("extract_title", True)
        self.generate_summary = self.config.get("generate_summary", True)
        self.extract_keywords = self.config.get("extract_keywords", True)
        self.max_keywords = self.config.get("max_keywords", 3)
        self.request_timeout = self.config.get("request_timeout", 10)
        self.user_agent = self.config.get(
            "user_agent", 
            "SmartPaste/0.1.0 (https://github.com/AbdHajjar/smartpaste)"
        )
        
        # Request session with retry configuration
        if WEB_SCRAPING_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
    
    def process(self, content: str) -> Optional[Dict[str, Any]]:
        """Process URL content.
        
        Args:
            content: URL string from clipboard
            
        Returns:
            Dictionary with processed URL information or None if processing fails
        """
        if not WEB_SCRAPING_AVAILABLE:
            self.logger.warning("Web scraping libraries not available")
            return {
                "original_content": content,
                "url": content,
                "title": "URL (title extraction unavailable)",
                "summary": "Install requests, readability-lxml, and beautifulsoup4 for full URL processing",
                "keywords": [],
                "enriched_content": content
            }
        
        # Clean and validate URL
        url = self._clean_url(content)
        if not url:
            return None
        
        try:
            # Fetch web page
            page_content = self._fetch_page(url)
            if not page_content:
                return None
            
            result = {
                "original_content": content,
                "url": url,
                "enriched_content": content
            }
            
            # Extract title
            if self.extract_title:
                title = self._extract_title(page_content, url)
                result["title"] = title
                result["enriched_content"] = f"{title}\\n{url}"
            
            # Extract and process text content
            text_content = self._extract_text_content(page_content)
            
            if text_content:
                # Generate summary
                if self.generate_summary:
                    summary = self._generate_summary(text_content)
                    result["summary"] = summary
                    if self.extract_title:
                        result["enriched_content"] = f"{title}\\n{summary}\\n{url}"
                
                # Extract keywords
                if self.extract_keywords:
                    keywords = self._extract_keywords(text_content)
                    result["keywords"] = keywords
                    if keywords and self.extract_title:
                        keywords_str = ", ".join(keywords)
                        result["enriched_content"] = f"{title}\\nKeywords: {keywords_str}\\n{summary}\\n{url}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {e}")
            return {
                "original_content": content,
                "url": url,
                "title": "URL (processing failed)",
                "summary": f"Error processing URL: {str(e)}",
                "keywords": [],
                "enriched_content": content
            }
    
    def _clean_url(self, content: str) -> Optional[str]:
        """Clean and validate URL.
        
        Args:
            content: Raw URL content
            
        Returns:
            Cleaned URL or None if invalid
        """
        url = content.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                url = 'https://' + url
            elif '.' in url and not url.startswith(('ftp://', 'file://')):
                url = 'https://' + url
            else:
                return None
        
        # Validate URL structure
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            return url
        except Exception:
            return None
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch web page content.
        
        Args:
            url: URL to fetch
            
        Returns:
            Page content as string or None if failed
        """
        try:
            response = self.session.get(
                url,
                timeout=self.request_timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(ct in content_type for ct in ['text/html', 'application/xhtml']):
                self.logger.debug(f"Skipping non-HTML content: {content_type}")
                return None
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Failed to fetch {url}: {e}")
            return None
    
    def _extract_title(self, page_content: str, url: str) -> str:
        """Extract page title.
        
        Args:
            page_content: HTML content
            url: Original URL for fallback
            
        Returns:
            Page title
        """
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Try different title sources in order of preference
            title_sources = [
                # Open Graph title
                soup.find('meta', property='og:title'),
                # Twitter title
                soup.find('meta', attrs={'name': 'twitter:title'}),
                # Standard title tag
                soup.find('title'),
                # H1 tag
                soup.find('h1')
            ]
            
            for source in title_sources:
                if source:
                    if source.name == 'meta':
                        title = source.get('content', '').strip()
                    else:
                        title = source.get_text().strip()
                    
                    if title:
                        return self._clean_title(title)
            
            # Fallback to URL
            parsed_url = urlparse(url)
            return f"Page from {parsed_url.netloc}"
            
        except Exception as e:
            self.logger.debug(f"Error extracting title: {e}")
            return f"Web Page"
    
    def _clean_title(self, title: str) -> str:
        """Clean extracted title.
        
        Args:
            title: Raw title string
            
        Returns:
            Cleaned title
        """
        # Remove common title suffixes
        suffixes = [
            r'\s*\|\s*.*$',  # Everything after |
            r'\s*-\s*.*$',    # Everything after -
            r'\s*—\s*.*$',    # Everything after em dash
            r'\s*::.*$',       # Everything after ::
        ]
        
        cleaned = title
        for suffix in suffixes:
            cleaned = re.sub(suffix, '', cleaned, count=1)
        
        # Clean whitespace and truncate if too long
        cleaned = re.sub(r'\\s+', ' ', cleaned).strip()
        if len(cleaned) > 100:
            cleaned = cleaned[:97] + "..."
        
        return cleaned if cleaned else title[:100]
    
    def _extract_text_content(self, page_content: str) -> Optional[str]:
        """Extract readable text content from HTML.
        
        Args:
            page_content: HTML content
            
        Returns:
            Extracted text content
        """
        try:
            # Use readability to extract main content
            doc = Document(page_content)
            readable_html = doc.summary()
            
            # Convert to plain text
            soup = BeautifulSoup(readable_html, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = [line.strip() for line in text.splitlines()]
            text = '\\n'.join(line for line in lines if line)
            
            # Remove excessive whitespace
            text = re.sub(r'\\n\\s*\\n', '\\n\\n', text)
            text = re.sub(r' +', ' ', text)
            
            return text.strip() if text.strip() else None
            
        except Exception as e:
            self.logger.debug(f"Error extracting text content: {e}")
            return None
    
    def _generate_summary(self, text_content: str) -> str:
        """Generate summary from text content.
        
        Args:
            text_content: Full text content
            
        Returns:
            Generated summary
        """
        if not text_content:
            return "No content available for summary."
        
        # Limit text length for processing
        if len(text_content) > 5000:
            text_content = text_content[:5000] + "..."
        
        try:
            summary = NLPUtils.summarize_text_simple(text_content, max_sentences=2)
            return summary if summary else "Content summary unavailable."
        except Exception as e:
            self.logger.debug(f"Error generating summary: {e}")
            return "Error generating summary."
    
    def _extract_keywords(self, text_content: str) -> List[str]:
        """Extract keywords from text content.
        
        Args:
            text_content: Full text content
            
        Returns:
            List of extracted keywords
        """
        if not text_content:
            return []
        
        try:
            # Use advanced keyword extraction if available, otherwise simple
            keywords = NLPUtils.extract_keywords_advanced(text_content, self.max_keywords)
            return keywords[:self.max_keywords]
        except Exception as e:
            self.logger.debug(f"Error extracting keywords: {e}")
            return []