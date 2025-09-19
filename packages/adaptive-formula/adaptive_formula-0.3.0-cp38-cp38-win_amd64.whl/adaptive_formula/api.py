import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import from compiled Cython module - now matches core.pyx exactly
from .core import AdaptiveFormula, Field as CoreField

# Public Field class - matches core.pyx API
class Field:
    """Public field configuration - matches core.pyx interface"""
    def __init__(self, name: str, reference: Any, importance: float = 1.0, sensitivity: float = 1.5):
        self.name = name
        self.reference = reference
        self.importance = importance
        self.sensitivity = sensitivity
    
    def to_dict(self):
        """Convert to internal format expected by AdaptiveFormula"""
        return {
            'default': self.reference,
            'weight': self.importance,
            'criticality': self.sensitivity
        }

class CognitiveSDK:
    """Public API for the Cognitive Programming SDK - matches core.pyx interface"""
    
    def __init__(self, tier: str = 'community', license_key: str = None):
        """Initialize SDK with tier and license validation"""
        self.tier = tier
        self.license_key = license_key
        self._formula = None
        self._config = {}
    
    def configure(self, fields: List[Field]):
        """Configure multiple fields at once - matches core.pyx"""
        self._config = {field.name: field.to_dict() for field in fields}
        self._formula = AdaptiveFormula(self._config, self.tier, self.license_key)
    
    def evaluate(self, data: Dict) -> float:
        """Evaluate data and return score - matches core.pyx"""
        if not self._formula:
            raise RuntimeError("SDK not configured. Call configure() first.")
        
        return self._formula.evaluate(data)
    
    def set_confidence_level(self, level: float):
        """Set decision confidence level - matches core.pyx"""
        if self._formula:
            self._formula.set_confidence_level(level)
    
    def get_confidence_level(self) -> float:
        """Get current confidence level - matches core.pyx"""
        return self._formula.get_confidence_level() if self._formula else 0.65
    
    def get_metrics(self) -> Dict:
        """Get performance metrics - matches core.pyx"""
        if not self._formula:
            return {'error': 'SDK not configured'}
        return self._formula.get_metrics()
    
    def process_heterogeneous(self, data):
        """Handle heterogeneous data - delegates to core.pyx"""
        if not self._formula:
            raise RuntimeError("SDK not configured. Call configure() first.")
        return self._formula.process_heterogeneous(data)
    
    def get_config(self) -> Dict:
        """Get current configuration (for debugging)"""
        return self._config.copy()
    
    def reset(self):
        """Reset configuration"""
        self._config = {}
        self._formula = None