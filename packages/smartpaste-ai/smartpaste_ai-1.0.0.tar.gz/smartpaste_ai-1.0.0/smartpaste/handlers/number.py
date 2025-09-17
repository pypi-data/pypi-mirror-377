"""
Number and unit conversion handler for SmartPaste.

This module handles numeric content with units by detecting numbers
and their units, then providing automatic conversions.
"""

import logging
import re
from typing import Dict, Any, Optional, List

from ..utils.nlp import NLPUtils


class NumberHandler:
    """Handler for number and unit conversion processing."""
    
    # Conversion factors to base units
    CONVERSION_FACTORS = {
        'temperature': {
            'base_unit': 'celsius',
            'conversions': {
                'celsius': 1.0,
                'c': 1.0,
                'fahrenheit': lambda c: c * 9/5 + 32,
                'f': lambda c: c * 9/5 + 32,
                'kelvin': lambda c: c + 273.15,
                'k': lambda c: c + 273.15,
            },
            'from_base': {
                'celsius': lambda c: c,
                'c': lambda c: c,
                'fahrenheit': lambda f: (f - 32) * 5/9,
                'f': lambda f: (f - 32) * 5/9,
                'kelvin': lambda k: k - 273.15,
                'k': lambda k: k - 273.15,
            }
        },
        'length': {
            'base_unit': 'meter',
            'conversions': {
                'meter': 1.0,
                'meters': 1.0,
                'm': 1.0,
                'kilometer': 0.001,
                'kilometers': 0.001,
                'km': 0.001,
                'centimeter': 100.0,
                'centimeters': 100.0,
                'cm': 100.0,
                'millimeter': 1000.0,
                'millimeters': 1000.0,
                'mm': 1000.0,
                'mile': 1/1609.344,
                'miles': 1/1609.344,
                'foot': 1/0.3048,
                'feet': 1/0.3048,
                'ft': 1/0.3048,
                'inch': 1/0.0254,
                'inches': 1/0.0254,
                'in': 1/0.0254,
            }
        },
        'weight': {
            'base_unit': 'kilogram',
            'conversions': {
                'kilogram': 1.0,
                'kilograms': 1.0,
                'kg': 1.0,
                'gram': 1000.0,
                'grams': 1000.0,
                'g': 1000.0,
                'milligram': 1000000.0,
                'milligrams': 1000000.0,
                'mg': 1000000.0,
                'pound': 1/0.453592,
                'pounds': 1/0.453592,
                'lb': 1/0.453592,
                'lbs': 1/0.453592,
                'ounce': 1/0.0283495,
                'ounces': 1/0.0283495,
                'oz': 1/0.0283495,
            }
        },
        'volume': {
            'base_unit': 'liter',
            'conversions': {
                'liter': 1.0,
                'liters': 1.0,
                'l': 1.0,
                'milliliter': 1000.0,
                'milliliters': 1000.0,
                'ml': 1000.0,
                'gallon': 1/3.78541,
                'gallons': 1/3.78541,
                'gal': 1/3.78541,
                'cup': 1/0.236588,
                'cups': 1/0.236588,
                'quart': 1/0.946353,
                'quarts': 1/0.946353,
                'qt': 1/0.946353,
                'pint': 1/0.473176,
                'pints': 1/0.473176,
                'pt': 1/0.473176,
                'fluid ounce': 1/0.0295735,
                'fluid ounces': 1/0.0295735,
                'fl oz': 1/0.0295735,
            }
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize number handler.
        
        Args:
            config: Configuration dictionary for number handling
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Get enabled conversions from config
        self.enabled_conversions = self.config.get("conversions", {})
        if not self.enabled_conversions:
            # Default to all conversions
            self.enabled_conversions = {
                "temperature": ["celsius", "fahrenheit", "kelvin"],
                "length": ["meter", "kilometer", "mile", "foot", "inch"],
                "weight": ["kilogram", "pound", "gram", "ounce"],
                "volume": ["liter", "gallon", "milliliter", "cup"]
            }
    
    def process(self, content: str) -> Optional[Dict[str, Any]]:
        """Process number content with units.
        
        Args:
            content: Text containing numbers with units
            
        Returns:
            Dictionary with conversion results or None if no numbers found
        """
        # Extract numbers with units
        numbers_with_units = NLPUtils.extract_numbers_with_units(content)
        
        if not numbers_with_units:
            return None
        
        results = []
        enriched_parts = []
        
        for item in numbers_with_units:
            value = item['value']
            unit = item['unit'].lower()
            unit_type = item['type']
            original = item['original']
            
            # Get conversions for this number
            conversions = self._get_conversions(value, unit, unit_type)
            
            if conversions:
                results.append({
                    'original_value': value,
                    'original_unit': unit,
                    'unit_type': unit_type,
                    'conversions': conversions
                })
                
                # Create enriched text
                conversion_text = self._format_conversions(value, unit, conversions)
                enriched_parts.append(f"{original} = {conversion_text}")
        
        if not results:
            return None
        
        # Create enriched content
        enriched_content = content
        if enriched_parts:
            enriched_content += "\\n\\nConversions:\\n" + "\\n".join(enriched_parts)
        
        return {
            "original_content": content,
            "numbers": results,
            "conversions": [conv for result in results for conv in result['conversions']],
            "enriched_content": enriched_content
        }
    
    def _get_conversions(
        self, 
        value: float, 
        unit: str, 
        unit_type: str
    ) -> List[Dict[str, Any]]:
        """Get conversions for a number with unit.
        
        Args:
            value: Numeric value
            unit: Unit string
            unit_type: Type of unit (temperature, length, etc.)
            
        Returns:
            List of conversion dictionaries
        """
        if unit_type not in self.CONVERSION_FACTORS:
            return []
        
        unit_config = self.CONVERSION_FACTORS[unit_type]
        enabled_units = self.enabled_conversions.get(unit_type, [])
        
        # Find the source unit in our conversion table
        source_unit = None
        for known_unit in unit_config['conversions']:
            if unit in [known_unit, known_unit.rstrip('s')]:  # Handle plurals
                source_unit = known_unit
                break
        
        if not source_unit:
            return []
        
        conversions = []
        
        # Special handling for temperature
        if unit_type == 'temperature':
            conversions = self._convert_temperature(value, unit, enabled_units)
        else:
            conversions = self._convert_standard_units(
                value, source_unit, unit_type, enabled_units
            )
        
        return conversions
    
    def _convert_temperature(
        self, 
        value: float, 
        unit: str, 
        enabled_units: List[str]
    ) -> List[Dict[str, Any]]:
        """Convert temperature values.
        
        Args:
            value: Temperature value
            unit: Source unit
            enabled_units: List of target units
            
        Returns:
            List of temperature conversions
        """
        conversions = []
        unit_lower = unit.lower()
        
        # Convert to celsius first
        if unit_lower in ['c', 'celsius']:
            celsius = value
        elif unit_lower in ['f', 'fahrenheit']:
            celsius = (value - 32) * 5/9
        elif unit_lower in ['k', 'kelvin']:
            celsius = value - 273.15
        else:
            return []
        
        # Convert from celsius to target units
        for target_unit in enabled_units:
            target_unit_lower = target_unit.lower()
            
            # Skip same unit
            if target_unit_lower == unit_lower or target_unit_lower in [unit_lower.rstrip('s'), unit_lower + 's']:
                continue
            
            if target_unit_lower in ['celsius', 'c']:
                converted_value = celsius
                display_unit = "°C"
            elif target_unit_lower in ['fahrenheit', 'f']:
                converted_value = celsius * 9/5 + 32
                display_unit = "°F"
            elif target_unit_lower in ['kelvin', 'k']:
                converted_value = celsius + 273.15
                display_unit = "K"
            else:
                continue
            
            conversions.append({
                'value': round(converted_value, 2),
                'unit': display_unit,
                'unit_name': target_unit_lower
            })
        
        return conversions
    
    def _convert_standard_units(
        self, 
        value: float, 
        source_unit: str, 
        unit_type: str, 
        enabled_units: List[str]
    ) -> List[Dict[str, Any]]:
        """Convert standard units (length, weight, volume).
        
        Args:
            value: Numeric value
            source_unit: Source unit
            unit_type: Type of unit
            enabled_units: List of target units
            
        Returns:
            List of conversions
        """
        conversions = []
        unit_config = self.CONVERSION_FACTORS[unit_type]
        
        # Convert to base unit first
        base_factor = unit_config['conversions'][source_unit]
        if callable(base_factor):
            base_value = base_factor(value)
        else:
            base_value = value / base_factor
        
        # Convert from base unit to target units
        for target_unit in enabled_units:
            target_unit_lower = target_unit.lower()
            
            # Skip same unit
            if target_unit_lower == source_unit.lower():
                continue
            
            # Find matching unit in conversion table
            target_factor = None
            for known_unit, factor in unit_config['conversions'].items():
                if target_unit_lower in [known_unit, known_unit.rstrip('s')]:
                    target_factor = factor
                    break
            
            if target_factor is None:
                continue
            
            # Convert from base unit
            if callable(target_factor):
                converted_value = target_factor(base_value)
            else:
                converted_value = base_value * target_factor
            
            # Format unit display
            display_unit = self._format_unit_display(target_unit_lower, converted_value)
            
            conversions.append({
                'value': round(converted_value, 4) if converted_value < 1 else round(converted_value, 2),
                'unit': display_unit,
                'unit_name': target_unit_lower
            })
        
        return conversions
    
    def _format_unit_display(self, unit: str, value: float) -> str:
        """Format unit for display.
        
        Args:
            unit: Unit name
            value: Numeric value
            
        Returns:
            Formatted unit string
        """
        # Unit abbreviations
        abbreviations = {
            'meter': 'm',
            'meters': 'm',
            'kilometer': 'km',
            'kilometers': 'km',
            'centimeter': 'cm',
            'centimeters': 'cm',
            'millimeter': 'mm',
            'millimeters': 'mm',
            'mile': 'mi',
            'miles': 'mi',
            'foot': 'ft',
            'feet': 'ft',
            'inch': 'in',
            'inches': 'in',
            'kilogram': 'kg',
            'kilograms': 'kg',
            'gram': 'g',
            'grams': 'g',
            'pound': 'lb',
            'pounds': 'lb',
            'ounce': 'oz',
            'ounces': 'oz',
            'liter': 'L',
            'liters': 'L',
            'milliliter': 'mL',
            'milliliters': 'mL',
            'gallon': 'gal',
            'gallons': 'gal',
            'cup': 'cup',
            'cups': 'cups',
        }
        
        return abbreviations.get(unit, unit)
    
    def _format_conversions(
        self, 
        original_value: float, 
        original_unit: str, 
        conversions: List[Dict[str, Any]]
    ) -> str:
        """Format conversions for display.
        
        Args:
            original_value: Original numeric value
            original_unit: Original unit
            conversions: List of conversion results
            
        Returns:
            Formatted conversion string
        """
        if not conversions:
            return ""
        
        conversion_strs = []
        for conv in conversions[:3]:  # Limit to 3 conversions
            value = conv['value']
            unit = conv['unit']
            conversion_strs.append(f"{value} {unit}")
        
        return ", ".join(conversion_strs)