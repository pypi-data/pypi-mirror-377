"""
Natural Language Processing utilities for SmartPaste.

This module provides NLP functionality including text analysis,
language detection, summarization, and keyword extraction.
"""

import re
import logging
from typing import List, Optional, Dict, Any, Tuple

try:
    from langdetect import detect, DetectorFactory
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ADVANCED_NLP_AVAILABLE = True
except ImportError:
    ADVANCED_NLP_AVAILABLE = False


class NLPUtils:
    """Utility class for NLP operations."""
    
    # Set deterministic seed for language detection
    if LANGDETECT_AVAILABLE:
        DetectorFactory.seed = 0
    
    # Language code to name mapping
    LANGUAGE_NAMES = {
        'en': 'English',
        'de': 'German', 
        'fr': 'French',
        'es': 'Spanish',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'pl': 'Polish',
        'cs': 'Czech',
        'tr': 'Turkish'
    }
    
    # Common units and their patterns
    UNIT_PATTERNS = {
        'temperature': [
            r'(?:^|\s)-?\d+(?:\.\d+)?\s*°?\s*[CcFfKk](?:\s|$)',
            r'(?:^|\s)-?\d+(?:\.\d+)?\s*(?:celsius|fahrenheit|kelvin)(?:\s|$)'
        ],
        'length': [
            r'(?:^|\s)-?\d+(?:\.\d+)?\s*(?:m|km|cm|mm|mile|miles|foot|feet|ft|inch|inches|in)(?:\s|$)',
            r'(?:^|\s)-?\d+(?:\.\d+)?\s*(?:meter|meters|kilometer|kilometers|centimeter|centimeters)(?:\s|$)'
        ],
        'weight': [
            r'(?:^|\s)-?\d+(?:\.\d+)?\s*(?:kg|g|mg|lb|lbs|oz|pound|pounds|gram|grams|kilogram|kilograms|ounce|ounces)(?:\s|$)'
        ],
        'volume': [
            r'(?:^|\s)-?\d+(?:\.\d+)?\s*(?:l|ml|gal|gallon|gallons|liter|liters|milliliter|milliliters|cup|cups)(?:\s|$)'
        ]
    }
    
    @staticmethod
    def detect_language(text: str) -> Optional[str]:
        """Detect the language of text.
        
        Args:
            text: Input text
            
        Returns:
            Language code or None if detection fails
        """
        if not LANGDETECT_AVAILABLE:
            logging.warning("langdetect not available, skipping language detection")
            return None
        
        if not text or len(text.strip()) < 10:
            return None
        
        try:
            lang_code = detect(text)
            return lang_code
        except Exception as e:
            logging.debug(f"Language detection failed: {e}")
            return None
    
    @staticmethod
    def get_language_name(lang_code: str) -> str:
        """Get human-readable language name from code.
        
        Args:
            lang_code: Language code (e.g., 'en', 'de')
            
        Returns:
            Language name or the code itself if unknown
        """
        return NLPUtils.LANGUAGE_NAMES.get(lang_code, lang_code)
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Extract sentences from text.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting on periods, exclamation marks, question marks
        # followed by whitespace and capital letter
        pattern = r'(?<=[.!?])\\s+(?=[A-Z])'
        sentences = re.split(pattern, text.strip())
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    @staticmethod
    def extract_keywords_simple(text: str, max_keywords: int = 5) -> List[str]:
        """Extract keywords using simple frequency analysis.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        # Remove punctuation and convert to lowercase
        words = re.findall(r'\\b[a-zA-Z]{3,}\\b', text.lower())
        
        # Common stop words to exclude
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'can', 'this', 'that', 'these', 'those', 'a', 'an', 'as', 'if', 'when',
            'where', 'why', 'how', 'what', 'who', 'which', 'than', 'then', 'now',
            'here', 'there', 'up', 'down', 'out', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'not', 'no', 'nor', 'too', 'very', 'more',
            'most', 'other', 'some', 'such', 'only', 'own', 'same', 'so', 'just'
        }
        
        # Filter out stop words and count frequencies
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    @staticmethod
    def extract_keywords_advanced(text: str, max_keywords: int = 5) -> List[str]:
        """Extract keywords using TF-IDF (requires scikit-learn).
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        if not ADVANCED_NLP_AVAILABLE:
            return NLPUtils.extract_keywords_simple(text, max_keywords)
        
        try:
            # Split into sentences for TF-IDF
            sentences = NLPUtils.extract_sentences(text)
            if len(sentences) < 2:
                return NLPUtils.extract_keywords_simple(text, max_keywords)
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )
            
            # Fit and transform
            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get average TF-IDF scores
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Sort by score and return top keywords
            keyword_scores = list(zip(feature_names, mean_scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return [keyword for keyword, score in keyword_scores[:max_keywords]]
            
        except Exception as e:
            logging.debug(f"Advanced keyword extraction failed: {e}")
            return NLPUtils.extract_keywords_simple(text, max_keywords)
    
    @staticmethod
    def summarize_text_simple(text: str, max_sentences: int = 3) -> str:
        """Create a simple extractive summary.
        
        Args:
            text: Input text
            max_sentences: Maximum number of sentences in summary
            
        Returns:
            Summary text
        """
        sentences = NLPUtils.extract_sentences(text)
        
        if len(sentences) <= max_sentences:
            return text.strip()
        
        # Simple heuristic: take first sentence, longest sentence, and last sentence
        if max_sentences == 1:
            return sentences[0]
        elif max_sentences == 2:
            return f"{sentences[0]} {sentences[-1]}"
        else:
            # First, longest, last
            longest_idx = max(range(len(sentences)), key=lambda i: len(sentences[i]))
            selected_indices = {0, longest_idx, len(sentences) - 1}
            
            # Add more sentences if needed
            while len(selected_indices) < max_sentences and len(selected_indices) < len(sentences):
                # Add sentence with highest keyword density
                remaining_indices = set(range(len(sentences))) - selected_indices
                if remaining_indices:
                    # Simple keyword density: number of unique words / sentence length
                    best_idx = max(remaining_indices, key=lambda i: 
                                 len(set(sentences[i].split())) / max(len(sentences[i]), 1))
                    selected_indices.add(best_idx)
            
            # Sort indices and join sentences
            sorted_indices = sorted(selected_indices)
            return ' '.join(sentences[i] for i in sorted_indices)
    
    @staticmethod
    def contains_number_with_unit(text: str) -> bool:
        """Check if text contains numbers with units.
        
        Args:
            text: Input text
            
        Returns:
            True if numbers with units are found
        """
        text_lower = text.lower()
        
        for unit_type, patterns in NLPUtils.UNIT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return True
        
        return False
    
    @staticmethod
    def extract_numbers_with_units(text: str) -> List[Dict[str, Any]]:
        """Extract numbers with their units from text.
        
        Args:
            text: Input text
            
        Returns:
            List of dictionaries with 'value', 'unit', and 'type' keys
        """
        results = []
        text_lower = text.lower()
        
        for unit_type, patterns in NLPUtils.UNIT_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    match_text = match.group()
                    
                    # Extract number and unit
                    number_match = re.search(r'-?\d+(?:\.\d+)?', match_text)
                    if number_match:
                        value = float(number_match.group())
                        unit = match_text.replace(number_match.group(), '').strip()
                        unit = re.sub(r'[°\s]+', '', unit)  # Clean unit
                        
                        results.append({
                            'value': value,
                            'unit': unit,
                            'type': unit_type,
                            'original': match.group()
                        })
        
        return results
    
    @staticmethod
    def calculate_text_stats(text: str) -> Dict[str, Any]:
        """Calculate basic text statistics.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with text statistics
        """
        sentences = NLPUtils.extract_sentences(text)
        words = text.split()
        characters = len(text)
        characters_no_spaces = len(text.replace(' ', ''))
        
        return {
            'character_count': characters,
            'character_count_no_spaces': characters_no_spaces,
            'word_count': len(words),
            'sentence_count': len(sentences),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'average_sentence_length': len(words) / len(sentences) if sentences else 0
        }