"""
I/O utilities for SmartPaste.

This module provides utilities for file operations, markdown generation,
and data persistence.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class IOUtils:
    """Utility class for I/O operations."""
    
    @staticmethod
    def ensure_directory(path: Path) -> None:
        """Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Path to the directory
        """
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def append_to_markdown(
        file_path: Path, 
        result: Dict[str, Any], 
        markdown_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Append a result to a markdown file.
        
        Args:
            file_path: Path to the markdown file
            result: Processed result to append
            markdown_config: Markdown formatting configuration
        """
        if markdown_config is None:
            markdown_config = {}
        
        # Ensure file exists
        IOUtils.ensure_directory(file_path.parent)
        
        # Check if file is new (needs header)
        is_new_file = not file_path.exists()
        
        with open(file_path, 'a', encoding='utf-8') as f:
            if is_new_file:
                # Add file header
                date_str = datetime.now().strftime("%Y-%m-%d")
                f.write(f"# SmartPaste - {date_str}\\n\\n")
                f.write("Auto-generated clipboard content analysis.\\n\\n")
                f.write("---\\n\\n")
            
            # Write the entry
            IOUtils._write_markdown_entry(f, result, markdown_config)
    
    @staticmethod
    def _write_markdown_entry(
        file_handle, 
        result: Dict[str, Any], 
        config: Dict[str, Any]
    ) -> None:
        """Write a single entry to markdown file.
        
        Args:
            file_handle: Open file handle
            result: Result data to write
            config: Markdown configuration
        """
        timestamp = result.get("timestamp", datetime.now().isoformat())
        content_type = result.get("content_type", "unknown")
        source = result.get("source", "unknown")
        
        # Entry header
        file_handle.write(f"## {timestamp} - {content_type.title()}\\n\\n")
        
        if config.get("include_source", True):
            file_handle.write(f"**Source:** {source}\\n\\n")
        
        # Main content
        original_content = result.get("original_content", "")
        if original_content:
            file_handle.write(f"**Original:**\\n```\\n{original_content[:500]}{'...' if len(original_content) > 500 else ''}\\n```\\n\\n")
        
        # Processed results
        IOUtils._write_processed_content(file_handle, result)
        
        file_handle.write("---\\n\\n")
    
    @staticmethod
    def _write_processed_content(file_handle, result: Dict[str, Any]) -> None:
        """Write processed content based on content type.
        
        Args:
            file_handle: Open file handle
            result: Result data
        """
        content_type = result.get("content_type", "")
        
        if content_type == "url":
            IOUtils._write_url_content(file_handle, result)
        elif content_type == "number":
            IOUtils._write_number_content(file_handle, result)
        elif content_type == "text":
            IOUtils._write_text_content(file_handle, result)
        elif content_type == "image":
            IOUtils._write_image_content(file_handle, result)
        else:
            # Generic content
            if "processed_content" in result:
                file_handle.write(f"**Processed:** {result['processed_content']}\\n\\n")
    
    @staticmethod
    def _write_url_content(file_handle, result: Dict[str, Any]) -> None:
        """Write URL-specific content."""
        if "title" in result:
            file_handle.write(f"**Title:** {result['title']}\\n\\n")
        
        if "summary" in result:
            file_handle.write(f"**Summary:** {result['summary']}\\n\\n")
        
        if "keywords" in result and result["keywords"]:
            keywords_str = ", ".join(result["keywords"])
            file_handle.write(f"**Keywords:** {keywords_str}\\n\\n")
        
        if "url" in result:
            file_handle.write(f"**Link:** [{result['url']}]({result['url']})\\n\\n")
    
    @staticmethod
    def _write_number_content(file_handle, result: Dict[str, Any]) -> None:
        """Write number conversion content."""
        if "original_value" in result:
            file_handle.write(f"**Original:** {result['original_value']} {result.get('original_unit', '')}\\n\\n")
        
        if "conversions" in result:
            file_handle.write("**Conversions:**\\n")
            for conversion in result["conversions"]:
                value = conversion.get("value", "")
                unit = conversion.get("unit", "")
                file_handle.write(f"- {value} {unit}\\n")
            file_handle.write("\\n")
    
    @staticmethod
    def _write_text_content(file_handle, result: Dict[str, Any]) -> None:
        """Write text analysis content."""
        if "language" in result:
            file_handle.write(f"**Language:** {result['language']}\\n\\n")
        
        if "summary" in result:
            file_handle.write(f"**Summary:** {result['summary']}\\n\\n")
        
        if "analysis" in result:
            analysis = result["analysis"]
            if "word_count" in analysis:
                file_handle.write(f"**Word Count:** {analysis['word_count']}\\n\\n")
    
    @staticmethod
    def _write_image_content(file_handle, result: Dict[str, Any]) -> None:
        """Write image OCR content."""
        if "extracted_text" in result:
            file_handle.write(f"**Extracted Text:**\\n```\\n{result['extracted_text']}\\n```\\n\\n")
        
        if "confidence" in result:
            file_handle.write(f"**OCR Confidence:** {result['confidence']}%\\n\\n")
    
    @staticmethod
    def save_json(file_path: Path, data: Dict[str, Any]) -> None:
        """Save data as JSON file.
        
        Args:
            file_path: Path to save the JSON file
            data: Data to save
        """
        IOUtils.ensure_directory(file_path.parent)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_json(file_path: Path) -> Optional[Dict[str, Any]]:
        """Load data from JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Loaded data or None if file doesn't exist
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    @staticmethod
    def read_text_file(file_path: Path) -> Optional[str]:
        """Read text from file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            File content or None if file doesn't exist
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError:
            return None