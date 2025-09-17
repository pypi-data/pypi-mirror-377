"""
Mathematical Expression Handler for SmartPaste.

This handler detects mathematical expressions, equations, and formulas
in clipboard content and provides parsing, evaluation, and formatting.
"""

import re
import math
import logging
from typing import Dict, Any, Optional, List, Union
from decimal import Decimal, InvalidOperation


class MathHandler:
    """Handler for detecting and processing mathematical expressions."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the math handler.
        
        Args:
            config: Configuration dictionary for the handler.
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.max_eval_length = self.config.get("max_eval_length", 1000)
        self.logger = logging.getLogger(__name__)
        
        # Mathematical patterns
        self.math_patterns = {
            "basic_arithmetic": r'[\d\s\+\-\*/\(\)\.]+',
            "equation": r'[a-zA-Z\d\s\+\-\*/\(\)\.\=\^]+',
            "scientific_notation": r'\d+(?:\.\d+)?[eE][+-]?\d+',
            "fractions": r'\d+/\d+',
            "percentages": r'\d+(?:\.\d+)?%',
            "square_root": r'√\d+|sqrt\(\d+\)',
            "powers": r'\d+\^\d+|\d+\*\*\d+',
            "trigonometric": r'(sin|cos|tan|asin|acos|atan)\([^)]+\)',
            "logarithmic": r'(log|ln|log10)\([^)]+\)',
            "constants": r'\b(pi|e|tau)\b',
        }
        
        # Math constants
        self.constants = {
            'pi': math.pi,
            'π': math.pi,
            'e': math.e,
            'tau': math.tau,
            'τ': math.tau,
        }
        
        # Safe mathematical functions
        self.safe_functions = {
            'abs': abs,
            'round': round,
            'floor': math.floor,
            'ceil': math.ceil,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pow': pow,
            'min': min,
            'max': max,
            'sum': sum,
        }
        
        # Mathematical units and conversions
        self.math_units = {
            'degrees': {'to_radians': lambda x: math.radians(x)},
            'radians': {'to_degrees': lambda x: math.degrees(x)},
            'celsius': {'to_fahrenheit': lambda x: (x * 9/5) + 32, 'to_kelvin': lambda x: x + 273.15},
            'fahrenheit': {'to_celsius': lambda x: (x - 32) * 5/9},
            'kelvin': {'to_celsius': lambda x: x - 273.15},
        }
    
    def process(self, content: str) -> Optional[Dict[str, Any]]:
        """Process content to detect and evaluate mathematical expressions.
        
        Args:
            content: The clipboard content to analyze.
            
        Returns:
            Dictionary with math analysis results or None if not mathematical.
        """
        if not self.enabled:
            return None
        
        content = content.strip()
        if not content or len(content) < 2:
            return None
        
        # Check if content contains mathematical expressions
        math_type = self._detect_math_type(content)
        if not math_type:
            return None
        
        try:
            result = {
                "original_content": content,
                "content_type": "math",
                "math_type": math_type,
            }
            
            # Extract and analyze mathematical expressions
            expressions = self._extract_expressions(content)
            result["expressions"] = expressions
            
            # Evaluate expressions if safe
            evaluated = self._evaluate_expressions(expressions)
            result["evaluations"] = evaluated
            
            # Detect mathematical concepts
            concepts = self._identify_concepts(content)
            result["concepts"] = concepts
            
            # Format results
            result["enriched_content"] = self._generate_enriched_content(result)
            
            self.logger.info(f"Processed {math_type} mathematical content with {len(expressions)} expressions")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing mathematical content: {e}")
            return None
    
    def _detect_math_type(self, content: str) -> Optional[str]:
        """Detect the type of mathematical content."""
        # Count different types of mathematical patterns
        pattern_counts = {}
        
        for pattern_name, pattern in self.math_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            pattern_counts[pattern_name] = len(matches)
        
        # Determine if content is mathematical
        total_math_patterns = sum(pattern_counts.values())
        
        # Simple heuristic: if we have mathematical patterns and the content
        # is mostly numbers, operators, and mathematical symbols
        math_chars = len(re.findall(r'[\d\+\-\*/\(\)\.\=\^\%√]', content))
        total_chars = len(content.replace(' ', '').replace('\n', ''))
        
        if total_chars > 0:
            math_ratio = math_chars / total_chars
            
            if math_ratio > 0.6 or total_math_patterns > 2:
                # Determine specific type
                if pattern_counts["equation"] > 0 and "=" in content:
                    return "equation"
                elif pattern_counts["trigonometric"] > 0:
                    return "trigonometry"
                elif pattern_counts["logarithmic"] > 0:
                    return "logarithmic"
                elif pattern_counts["basic_arithmetic"] > 0:
                    return "arithmetic"
                elif pattern_counts["scientific_notation"] > 0:
                    return "scientific"
                else:
                    return "general_math"
        
        return None
    
    def _extract_expressions(self, content: str) -> List[Dict[str, Any]]:
        """Extract individual mathematical expressions from content."""
        expressions = []
        
        # Split content into potential expressions
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Check each pattern type
            for pattern_name, pattern in self.math_patterns.items():
                matches = re.finditer(pattern, line)
                for match in matches:
                    expr_text = match.group().strip()
                    if len(expr_text) > 1:  # Avoid single characters
                        expressions.append({
                            "text": expr_text,
                            "line": line_num,
                            "type": pattern_name,
                            "start": match.start(),
                            "end": match.end(),
                        })
        
        # Remove duplicates and sort by position
        seen = set()
        unique_expressions = []
        for expr in expressions:
            key = (expr["text"], expr["line"])
            if key not in seen:
                seen.add(key)
                unique_expressions.append(expr)
        
        return sorted(unique_expressions, key=lambda x: (x["line"], x["start"]))
    
    def _evaluate_expressions(self, expressions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Safely evaluate mathematical expressions."""
        evaluated = []
        
        for expr in expressions:
            expr_text = expr["text"]
            result = {
                "expression": expr_text,
                "type": expr["type"],
                "evaluated": False,
                "result": None,
                "error": None,
            }
            
            try:
                # Skip if expression is too long (security)
                if len(expr_text) > self.max_eval_length:
                    result["error"] = "Expression too long"
                    evaluated.append(result)
                    continue
                
                # Try different evaluation strategies based on type
                if expr["type"] == "basic_arithmetic":
                    result.update(self._evaluate_arithmetic(expr_text))
                elif expr["type"] == "equation":
                    result.update(self._evaluate_equation(expr_text))
                elif expr["type"] == "fractions":
                    result.update(self._evaluate_fraction(expr_text))
                elif expr["type"] == "percentages":
                    result.update(self._evaluate_percentage(expr_text))
                elif expr["type"] == "scientific_notation":
                    result.update(self._evaluate_scientific(expr_text))
                elif expr["type"] in ["trigonometric", "logarithmic"]:
                    result.update(self._evaluate_function(expr_text))
                
            except Exception as e:
                result["error"] = str(e)
            
            evaluated.append(result)
        
        return evaluated
    
    def _evaluate_arithmetic(self, expr: str) -> Dict[str, Any]:
        """Evaluate basic arithmetic expression."""
        try:
            # Clean the expression
            cleaned = re.sub(r'[^\d\+\-\*/\(\)\.]', '', expr)
            
            # Replace constants
            for const, value in self.constants.items():
                cleaned = cleaned.replace(const, str(value))
            
            # Evaluate safely
            if self._is_safe_expression(cleaned):
                result = eval(cleaned)
                return {
                    "evaluated": True,
                    "result": result,
                    "formatted_result": self._format_number(result),
                }
            else:
                return {"error": "Unsafe expression"}
                
        except Exception as e:
            return {"error": f"Evaluation error: {str(e)}"}
    
    def _evaluate_equation(self, expr: str) -> Dict[str, Any]:
        """Evaluate equation (handle both sides of =)."""
        if "=" not in expr:
            return {"error": "No equals sign found"}
        
        try:
            left, right = expr.split("=", 1)
            left_result = self._evaluate_arithmetic(left.strip())
            right_result = self._evaluate_arithmetic(right.strip())
            
            if left_result.get("evaluated") and right_result.get("evaluated"):
                left_val = left_result["result"]
                right_val = right_result["result"]
                
                return {
                    "evaluated": True,
                    "left_side": left_val,
                    "right_side": right_val,
                    "balanced": abs(left_val - right_val) < 1e-10,
                    "difference": abs(left_val - right_val),
                }
            else:
                return {"error": "Could not evaluate both sides"}
                
        except Exception as e:
            return {"error": f"Equation error: {str(e)}"}
    
    def _evaluate_fraction(self, expr: str) -> Dict[str, Any]:
        """Evaluate fraction expression."""
        try:
            match = re.match(r'(\d+)/(\d+)', expr)
            if match:
                numerator = int(match.group(1))
                denominator = int(match.group(2))
                
                if denominator == 0:
                    return {"error": "Division by zero"}
                
                decimal_result = numerator / denominator
                
                return {
                    "evaluated": True,
                    "numerator": numerator,
                    "denominator": denominator,
                    "decimal": decimal_result,
                    "percentage": decimal_result * 100,
                    "simplified": self._simplify_fraction(numerator, denominator),
                }
            else:
                return {"error": "Invalid fraction format"}
                
        except Exception as e:
            return {"error": f"Fraction error: {str(e)}"}
    
    def _evaluate_percentage(self, expr: str) -> Dict[str, Any]:
        """Evaluate percentage expression."""
        try:
            match = re.match(r'(\d+(?:\.\d+)?)%', expr)
            if match:
                value = float(match.group(1))
                
                return {
                    "evaluated": True,
                    "percentage": value,
                    "decimal": value / 100,
                    "fraction": f"{int(value)}/100" if value == int(value) else f"{value}/100",
                }
            else:
                return {"error": "Invalid percentage format"}
                
        except Exception as e:
            return {"error": f"Percentage error: {str(e)}"}
    
    def _evaluate_scientific(self, expr: str) -> Dict[str, Any]:
        """Evaluate scientific notation."""
        try:
            value = float(expr)
            
            return {
                "evaluated": True,
                "scientific": expr,
                "decimal": value,
                "formatted": self._format_number(value),
            }
            
        except Exception as e:
            return {"error": f"Scientific notation error: {str(e)}"}
    
    def _evaluate_function(self, expr: str) -> Dict[str, Any]:
        """Evaluate mathematical function."""
        try:
            # This is a simplified version - in practice, you'd want
            # a more robust mathematical expression parser
            for func_name, func in self.safe_functions.items():
                if func_name in expr.lower():
                    # Extract the argument (simplified)
                    match = re.search(rf'{func_name}\s*\(\s*([^)]+)\s*\)', expr, re.IGNORECASE)
                    if match:
                        arg_str = match.group(1)
                        arg_result = self._evaluate_arithmetic(arg_str)
                        
                        if arg_result.get("evaluated"):
                            result = func(arg_result["result"])
                            return {
                                "evaluated": True,
                                "function": func_name,
                                "argument": arg_result["result"],
                                "result": result,
                                "formatted_result": self._format_number(result),
                            }
            
            return {"error": "Function not recognized"}
            
        except Exception as e:
            return {"error": f"Function error: {str(e)}"}
    
    def _is_safe_expression(self, expr: str) -> bool:
        """Check if expression is safe to evaluate."""
        # Basic safety check - no imports, no dangerous functions
        dangerous_patterns = [
            r'__import__', r'eval', r'exec', r'open', r'file',
            r'input', r'raw_input', r'compile', r'globals',
            r'locals', r'vars', r'dir', r'help'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, expr, re.IGNORECASE):
                return False
        
        return True
    
    def _simplify_fraction(self, numerator: int, denominator: int) -> str:
        """Simplify a fraction to lowest terms."""
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        common_divisor = gcd(numerator, denominator)
        simplified_num = numerator // common_divisor
        simplified_den = denominator // common_divisor
        
        if simplified_den == 1:
            return str(simplified_num)
        else:
            return f"{simplified_num}/{simplified_den}"
    
    def _format_number(self, number: Union[int, float]) -> str:
        """Format number for display."""
        if isinstance(number, int):
            return str(number)
        elif abs(number) >= 1e6 or abs(number) <= 1e-4:
            return f"{number:.3e}"
        else:
            return f"{number:.6f}".rstrip('0').rstrip('.')
    
    def _identify_concepts(self, content: str) -> List[str]:
        """Identify mathematical concepts in the content."""
        concepts = []
        
        concept_patterns = {
            "algebra": [r'[a-zA-Z]\s*=', r'[a-zA-Z]\^2', r'[a-zA-Z]\s*\+\s*[a-zA-Z]'],
            "geometry": [r'area|perimeter|volume|radius|diameter|circumference', r'π|pi'],
            "trigonometry": [r'sin|cos|tan|sec|csc|cot', r'degrees|radians'],
            "calculus": [r'derivative|integral|limit|∂|∫|lim'],
            "statistics": [r'mean|median|mode|std|variance|correlation'],
            "probability": [r'probability|chance|odds|random'],
            "linear_algebra": [r'matrix|vector|determinant|eigenvalue'],
            "number_theory": [r'prime|factor|gcd|lcm|modulo'],
        }
        
        for concept, patterns in concept_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    concepts.append(concept)
                    break
        
        return list(set(concepts))
    
    def _generate_enriched_content(self, result: Dict[str, Any]) -> str:
        """Generate enriched version of the mathematical content."""
        math_type = result["math_type"]
        expressions = result["expressions"]
        evaluations = result["evaluations"]
        concepts = result["concepts"]
        
        header = f"# Mathematical Analysis: {math_type.title()}\n\n"
        
        if concepts:
            concept_info = f"**Concepts:** {', '.join(concepts)}\n"
        else:
            concept_info = ""
        
        summary = (
            f"**Type:** {math_type.title()}\n"
            f"**Expressions Found:** {len(expressions)}\n"
            f"**Successfully Evaluated:** {sum(1 for e in evaluations if e.get('evaluated'))}\n"
            f"{concept_info}\n"
        )
        
        # Show original content
        original = f"## Original Content:\n```\n{result['original_content']}\n```\n\n"
        
        # Show evaluations
        eval_section = "## Evaluations:\n"
        for eval_result in evaluations:
            if eval_result.get("evaluated"):
                if eval_result.get("result") is not None:
                    eval_section += f"- `{eval_result['expression']}` = **{eval_result.get('formatted_result', eval_result['result'])}**\n"
                elif eval_result.get("balanced") is not None:
                    balance_status = "✅ Balanced" if eval_result["balanced"] else "❌ Not balanced"
                    eval_section += f"- `{eval_result['expression']}` → {balance_status}\n"
            else:
                error = eval_result.get("error", "Unknown error")
                eval_section += f"- `{eval_result['expression']}` → ❌ {error}\n"
        
        return header + summary + original + eval_section