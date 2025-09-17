"""
Code Detection and Analysis Handler for SmartPaste.

This handler detects programming code in clipboard content and provides
language identification, syntax highlighting info, and code analysis.
"""

import re
import logging
from typing import Dict, Any, Optional, List
import keyword


class CodeHandler:
    """Handler for detecting and analyzing programming code content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the code handler.
        
        Args:
            config: Configuration dictionary for the handler.
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.logger = logging.getLogger(__name__)
        
        # Language detection patterns
        self.language_patterns = {
            "python": [
                r"def\s+\w+\s*\(",
                r"class\s+\w+\s*\(",
                r"import\s+\w+",
                r"from\s+\w+\s+import",
                r"if\s+__name__\s*==\s*['\"]__main__['\"]",
                r"print\s*\(",
                r"@\w+",  # decorators
            ],
            "javascript": [
                r"function\s+\w+\s*\(",
                r"const\s+\w+\s*=",
                r"let\s+\w+\s*=",
                r"var\s+\w+\s*=",
                r"=>\s*{",
                r"require\s*\(",
                r"module\.exports",
                r"console\.log\s*\(",
            ],
            "typescript": [
                r"interface\s+\w+",
                r"type\s+\w+\s*=",
                r":\s*\w+\s*=",
                r"<\w+>",
                r"implements\s+\w+",
                r"export\s+(interface|type|class)",
            ],
            "java": [
                r"public\s+(class|interface)",
                r"private\s+\w+",
                r"protected\s+\w+",
                r"import\s+java\.",
                r"@Override",
                r"System\.out\.println",
                r"public\s+static\s+void\s+main",
            ],
            "cpp": [
                r"#include\s*<",
                r"std::",
                r"cout\s*<<",
                r"cin\s*>>",
                r"using\s+namespace",
                r"int\s+main\s*\(",
                r"\w+\s*::\s*\w+",
            ],
            "csharp": [
                r"using\s+System",
                r"namespace\s+\w+",
                r"public\s+class\s+\w+",
                r"Console\.WriteLine",
                r"\[.*\]",  # attributes
                r"get\s*;\s*set\s*;",
            ],
            "html": [
                r"<html",
                r"<head>",
                r"<body>",
                r"<div",
                r"<!DOCTYPE",
                r"<script",
                r"<style",
            ],
            "css": [
                r"\.\w+\s*{",
                r"#\w+\s*{",
                r"\w+\s*:\s*\w+;",
                r"@media",
                r"@import",
                r"!important",
            ],
            "sql": [
                r"SELECT\s+.*\s+FROM",
                r"INSERT\s+INTO",
                r"UPDATE\s+.*\s+SET",
                r"DELETE\s+FROM",
                r"CREATE\s+TABLE",
                r"ALTER\s+TABLE",
                r"WHERE\s+",
            ],
            "json": [
                r"^\s*{",
                r"^\s*\[",
                r'"\w+"\s*:',
                r':\s*".*"',
                r':\s*\d+',
                r':\s*(true|false|null)',
            ],
            "xml": [
                r"<\?xml",
                r"<!\[CDATA\[",
                r"</\w+>",
                r"<\w+.*/>",
                r"xmlns:",
            ],
            "bash": [
                r"#!/bin/bash",
                r"#!/bin/sh",
                r"\$\w+",
                r"echo\s+",
                r"grep\s+",
                r"sed\s+",
                r"awk\s+",
            ],
            "powershell": [
                r"Get-\w+",
                r"Set-\w+",
                r"New-\w+",
                r"\$\w+",
                r"-\w+\s+",
                r"Write-Host",
                r"Import-Module",
            ],
            "yaml": [
                r"^\s*\w+:",
                r"^\s*-\s+\w+",
                r"---",
                r"\${",
                r"apiVersion:",
                r"kind:",
            ],
            "markdown": [
                r"^#+\s+",
                r"\*\*.*\*\*",
                r"\*.*\*",
                r"`.*`",
                r"\[.*\]\(.*\)",
                r"^-\s+",
                r"^>\s+",
            ],
        }
        
        # Code quality indicators
        self.quality_patterns = {
            "comments": [
                r"#.*",  # Python, bash
                r"//.*",  # JS, Java, C++
                r"/\*.*\*/",  # Multi-line comments
                r"<!--.*-->",  # HTML
            ],
            "imports": [
                r"import\s+",
                r"require\s*\(",
                r"#include",
                r"using\s+",
            ],
            "functions": [
                r"def\s+\w+",
                r"function\s+\w+",
                r"\w+\s*\([^)]*\)\s*{",
            ],
            "classes": [
                r"class\s+\w+",
                r"interface\s+\w+",
                r"struct\s+\w+",
            ],
        }
    
    def process(self, content: str) -> Optional[Dict[str, Any]]:
        """Process content to detect and analyze code.
        
        Args:
            content: The clipboard content to analyze.
            
        Returns:
            Dictionary with code analysis results or None if not code.
        """
        if not self.enabled:
            return None
        
        content = content.strip()
        if not content or len(content) < 10:
            return None
        
        # Check if content looks like code
        if not self._is_code_content(content):
            return None
        
        try:
            # Detect programming language
            detected_language = self._detect_language(content)
            
            # Analyze code structure
            analysis = self._analyze_code_structure(content)
            
            # Calculate code metrics
            metrics = self._calculate_metrics(content)
            
            result = {
                "original_content": content,
                "content_type": "code",
                "detected_language": detected_language,
                "confidence": analysis.get("confidence", 0),
                "structure": analysis,
                "metrics": metrics,
                "enriched_content": self._generate_enriched_content(
                    content, detected_language, analysis, metrics
                ),
            }
            
            self.logger.info(f"Detected {detected_language} code with {len(content)} characters")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing code content: {e}")
            return None
    
    def _is_code_content(self, content: str) -> bool:
        """Check if content appears to be programming code."""
        # Basic heuristics for code detection
        indicators = 0
        
        # Check for common code patterns
        code_indicators = [
            r"{.*}",  # Braces
            r"\[.*\]",  # Brackets
            r"\(.*\)",  # Parentheses
            r"=.*[;,]",  # Assignments
            r"if\s*\(",  # Conditionals
            r"for\s*\(",  # Loops
            r"function|def|class",  # Keywords
            r"#include|import|require",  # Imports
            r"[a-zA-Z_]\w*\s*\(",  # Function calls
        ]
        
        for pattern in code_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                indicators += 1
        
        # Check for indentation patterns (common in code)
        lines = content.split('\n')
        indented_lines = sum(1 for line in lines if line.startswith(('    ', '\t')))
        if len(lines) > 3 and indented_lines / len(lines) > 0.3:
            indicators += 2
        
        # Check for semicolons or specific operators
        if ';' in content or '->' in content or '=>' in content:
            indicators += 1
        
        return indicators >= 3
    
    def _detect_language(self, content: str) -> str:
        """Detect the programming language of the code."""
        scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
                score += matches
            scores[language] = score
        
        # Return language with highest score, or 'unknown' if no clear winner
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                return max(scores.keys(), key=scores.get)
        
        return "unknown"
    
    def _analyze_code_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure and components of the code."""
        structure = {
            "lines": len(content.split('\n')),
            "characters": len(content),
            "confidence": 0,
        }
        
        # Count different code elements
        for element_type, patterns in self.quality_patterns.items():
            count = 0
            for pattern in patterns:
                count += len(re.findall(pattern, content, re.IGNORECASE))
            structure[f"{element_type}_count"] = count
        
        # Calculate confidence based on detected elements
        total_elements = sum(
            structure.get(f"{key}_count", 0) 
            for key in self.quality_patterns.keys()
        )
        structure["confidence"] = min(100, total_elements * 10)
        
        return structure
    
    def _calculate_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate code quality and complexity metrics."""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        return {
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty_lines),
            "average_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0,
            "max_line_length": max(len(line) for line in lines) if lines else 0,
            "indentation_levels": self._count_indentation_levels(lines),
            "complexity_estimate": self._estimate_complexity(content),
        }
    
    def _count_indentation_levels(self, lines: List[str]) -> int:
        """Count the number of different indentation levels."""
        indentations = set()
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indentations.add(indent)
        return len(indentations)
    
    def _estimate_complexity(self, content: str) -> str:
        """Estimate the complexity of the code."""
        complexity_indicators = [
            r"if\s*\(",
            r"for\s*\(",
            r"while\s*\(",
            r"switch\s*\(",
            r"case\s+",
            r"catch\s*\(",
            r"try\s*{",
        ]
        
        total_complexity = 0
        for pattern in complexity_indicators:
            total_complexity += len(re.findall(pattern, content, re.IGNORECASE))
        
        if total_complexity == 0:
            return "simple"
        elif total_complexity <= 5:
            return "moderate"
        elif total_complexity <= 15:
            return "complex"
        else:
            return "very_complex"
    
    def _generate_enriched_content(self, content: str, language: str, 
                                 structure: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Generate enriched version of the code content."""
        header = f"# Code Analysis: {language.title()}\n\n"
        
        stats = (
            f"**Language:** {language.title()}\n"
            f"**Lines:** {metrics['total_lines']} ({metrics['non_empty_lines']} non-empty)\n"
            f"**Complexity:** {metrics['complexity_estimate'].title()}\n"
            f"**Functions:** {structure.get('functions_count', 0)}\n"
            f"**Classes:** {structure.get('classes_count', 0)}\n"
            f"**Comments:** {structure.get('comments_count', 0)}\n\n"
        )
        
        code_block = f"```{language}\n{content}\n```\n"
        
        return header + stats + code_block