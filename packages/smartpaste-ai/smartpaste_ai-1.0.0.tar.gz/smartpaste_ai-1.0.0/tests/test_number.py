"""
Tests for number handler functionality.
"""

import pytest
from smartpaste.handlers.number import NumberHandler


class TestNumberHandler:
    """Test cases for NumberHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "conversions": {
                "temperature": ["celsius", "fahrenheit", "kelvin"],
                "length": ["meter", "kilometer", "mile", "foot"],
                "weight": ["kilogram", "pound", "gram"],
                "volume": ["liter", "gallon", "milliliter"]
            }
        }
        self.handler = NumberHandler(self.config)
    
    def test_temperature_conversion_celsius(self):
        """Test temperature conversion from Celsius."""
        content = "25°C"
        result = self.handler.process(content)
        
        assert result is not None
        assert len(result["numbers"]) == 1
        assert result["numbers"][0]["original_value"] == 25.0
        assert result["numbers"][0]["unit_type"] == "temperature"
        
        # Check conversions
        conversions = result["numbers"][0]["conversions"]
        fahrenheit_conversion = next((c for c in conversions if c["unit"] == "°F"), None)
        kelvin_conversion = next((c for c in conversions if c["unit"] == "K"), None)
        
        assert fahrenheit_conversion is not None
        assert fahrenheit_conversion["value"] == 77.0
        assert kelvin_conversion is not None
        assert kelvin_conversion["value"] == 298.15
    
    def test_temperature_conversion_fahrenheit(self):
        """Test temperature conversion from Fahrenheit."""
        content = "77°F"
        result = self.handler.process(content)
        
        assert result is not None
        conversions = result["numbers"][0]["conversions"]
        celsius_conversion = next((c for c in conversions if c["unit"] == "°C"), None)
        
        assert celsius_conversion is not None
        assert celsius_conversion["value"] == 25.0
    
    def test_length_conversion_meters(self):
        """Test length conversion from meters."""
        content = "1000 meters"
        result = self.handler.process(content)
        
        assert result is not None
        assert result["numbers"][0]["original_value"] == 1000.0
        assert result["numbers"][0]["unit_type"] == "length"
        
        conversions = result["numbers"][0]["conversions"]
        km_conversion = next((c for c in conversions if c["unit"] == "km"), None)
        
        assert km_conversion is not None
        assert km_conversion["value"] == 1.0
    
    def test_weight_conversion_kilograms(self):
        """Test weight conversion from kilograms."""
        content = "10 kg"
        result = self.handler.process(content)
        
        assert result is not None
        conversions = result["numbers"][0]["conversions"]
        pound_conversion = next((c for c in conversions if c["unit"] == "lb"), None)
        
        assert pound_conversion is not None
        assert abs(pound_conversion["value"] - 22.05) < 0.1  # Allow small floating point differences
    
    def test_volume_conversion_liters(self):
        """Test volume conversion from liters."""
        content = "5 liters"
        result = self.handler.process(content)
        
        assert result is not None
        conversions = result["numbers"][0]["conversions"]
        gallon_conversion = next((c for c in conversions if c["unit"] == "gal"), None)
        
        assert gallon_conversion is not None
        assert abs(gallon_conversion["value"] - 1.32) < 0.1
    
    def test_multiple_numbers(self):
        """Test processing multiple numbers in one text."""
        content = "Temperature is 25°C and distance is 5 km"
        result = self.handler.process(content)
        
        assert result is not None
        assert len(result["numbers"]) == 2
        
        # Check that we have both temperature and length conversions
        unit_types = [num["unit_type"] for num in result["numbers"]]
        assert "temperature" in unit_types
        assert "length" in unit_types
    
    def test_no_numbers_found(self):
        """Test processing text with no numbers and units."""
        content = "This is just plain text without any measurements."
        result = self.handler.process(content)
        
        assert result is None
    
    def test_number_without_unit(self):
        """Test processing numbers without units."""
        content = "The answer is 42"
        result = self.handler.process(content)
        
        assert result is None
    
    def test_invalid_unit(self):
        """Test processing numbers with invalid units."""
        content = "25 xyz"
        result = self.handler.process(content)
        
        assert result is None
    
    def test_format_unit_display(self):
        """Test unit display formatting."""
        # Test abbreviations
        assert self.handler._format_unit_display("meter", 1) == "m"
        assert self.handler._format_unit_display("kilometer", 1) == "km"
        assert self.handler._format_unit_display("kilogram", 1) == "kg"
        assert self.handler._format_unit_display("liter", 1) == "L"
        
        # Test unknown unit
        assert self.handler._format_unit_display("unknown", 1) == "unknown"
    
    def test_enriched_content_generation(self):
        """Test enriched content generation."""
        content = "The temperature is 25°C"
        result = self.handler.process(content)
        
        assert result is not None
        enriched = result["enriched_content"]
        
        assert "Conversions:" in enriched
        assert "25°C" in enriched
        assert "°F" in enriched or "°K" in enriched  # Should have at least one conversion


class TestNumberHandlerEdgeCases:
    """Test edge cases for NumberHandler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = NumberHandler()
    
    def test_decimal_numbers(self):
        """Test processing decimal numbers."""
        content = "3.14 meters"
        result = self.handler.process(content)
        
        assert result is not None
        assert result["numbers"][0]["original_value"] == 3.14
    
    def test_zero_values(self):
        """Test processing zero values."""
        content = "0°C"
        result = self.handler.process(content)
        
        assert result is not None
        conversions = result["numbers"][0]["conversions"]
        fahrenheit_conversion = next((c for c in conversions if c["unit"] == "°F"), None)
        
        assert fahrenheit_conversion is not None
        assert fahrenheit_conversion["value"] == 32.0
    
    def test_negative_temperatures(self):
        """Test processing negative temperatures."""
        content = "-10°C"
        result = self.handler.process(content)
        
        assert result is not None
        conversions = result["numbers"][0]["conversions"]
        fahrenheit_conversion = next((c for c in conversions if c["unit"] == "°F"), None)
        
        assert fahrenheit_conversion is not None
        assert fahrenheit_conversion["value"] == 14.0
    
    def test_unit_variations(self):
        """Test different unit formats and variations."""
        test_cases = [
            "25 C",
            "25°C",
            "25 celsius",
            "25 Celsius",
        ]
        
        for content in test_cases:
            result = self.handler.process(content)
            assert result is not None, f"Failed to process: {content}"
    
    def test_handler_initialization_no_config(self):
        """Test handler initialization without configuration."""
        handler = NumberHandler()
        
        # Should use default conversions
        assert "temperature" in handler.enabled_conversions
        assert "length" in handler.enabled_conversions
        assert "weight" in handler.enabled_conversions
        assert "volume" in handler.enabled_conversions
    
    def test_large_numbers(self):
        """Test processing very large numbers."""
        content = "1000000 meters"
        result = self.handler.process(content)
        
        assert result is not None
        assert result["numbers"][0]["original_value"] == 1000000.0
        
        conversions = result["numbers"][0]["conversions"]
        km_conversion = next((c for c in conversions if c["unit"] == "km"), None)
        
        assert km_conversion is not None
        assert km_conversion["value"] == 1000.0