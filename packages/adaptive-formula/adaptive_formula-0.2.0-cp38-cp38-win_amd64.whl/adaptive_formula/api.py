import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# These will be imported from compiled Cython module
from .core import AdaptiveFormula
from .license import LicenseValidator
from .models import LicenseTier, FieldConfig

@dataclass
class Field:
    """Public field configuration"""
    name: str
    default: Any
    weight: float = 1.0
    criticality: float = 1.5

class CognitiveSDK:
    """Public API for the Cognitive Programming SDK"""
    
    def __init__(self, license_key: Optional[str] = None):
        """Initialize SDK with license validation"""
        self.license_key = license_key or os.getenv('ADAPTIVE_FORMULA_KEY', 'community')
        self.validator = LicenseValidator()
        
        # Validate and get tier
        validation = self.validator.validate(self.license_key)
        if not validation['valid']:
            raise ValueError(f"Invalid license: {validation.get('error', 'Unknown error')}")
        
        self.tier = validation['tier']
        self.remaining_calls = validation.get('remaining_calls')
        self._formula = None
        self._config = {}
        self._call_count = 0
    
    def add_field(self, field: Field):
        """Add field configuration"""
        self._config[field.name] = {
            'default': field.default,
            'weight': field.weight,
            'criticality': field.criticality
        }
    
    def configure(self, fields: List[Field]):
        """Configure multiple fields at once"""
        for field in fields:
            self.add_field(field)
        # Reset formula to apply new config
        self._formula = None
    
    def evaluate(self, data: Any) -> float:
        """Evaluate data and return score"""
        # Check call limits for community tier
        if self.tier == 'community':
            self._call_count += 1
            if self.remaining_calls is not None:
                if self.remaining_calls <= 0:
                    raise ValueError("Call limit exceeded. Upgrade to Professional or Enterprise.")
                self.remaining_calls -= 1
            elif self._call_count > 1000:
                raise ValueError("Monthly limit reached. Upgrade to Professional or Enterprise.")
        
        # Initialize formula if needed
        if not self._formula:
            self._formula = AdaptiveFormula(self._config, self.tier)
        
        # Process heterogeneous data if supported
        if self.tier != 'community':
            data = self._formula.process_heterogeneous(data)
        elif not isinstance(data, dict):
            raise TypeError("Community tier only supports dictionary data")
        
        # Calculate score
        score = self._formula.evaluate(data)
        
        # Track usage asynchronously
        if self._call_count % 10 == 0:  # Batch tracking
            self.validator.track_usage(self.license_key, 10)
        
        return score
    
    def auto_calibrate(self, historical_data: List[Dict]) -> None:
        """Auto-calibrate using ML - Pro/Enterprise only"""
        if self.tier == 'community':
            raise ValueError("Auto-calibration requires Professional or Enterprise license")
        
        # Simulated ML calibration
        # In production, this would adjust weights based on historical patterns
        print(f"Auto-calibrating with {len(historical_data)} samples...")
        
        # This would call into protected ML logic in core.pyx
        for field_name in self._config:
            # Simulate optimization
            self._config[field_name]['weight'] *= 1.1
            self._config[field_name]['criticality'] *= 0.95
        
        # Reset formula with new config
        self._formula = None
    
    def get_config(self) -> Dict:
        """Get current configuration (for debugging)"""
        return self._config.copy()
    
    def reset(self):
        """Reset configuration"""
        self._config = {}
        self._formula = None
        self._call_count = 0