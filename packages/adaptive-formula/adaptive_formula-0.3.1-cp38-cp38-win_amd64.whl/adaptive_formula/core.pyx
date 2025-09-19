# cython: language_level=3
# distutils: language=c++

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
cimport numpy as np
from libc.math cimport fabs

# Public Field class for configuration
class Field:
    """Field configuration for adaptive formula"""
    def __init__(self, name: str, reference: Any, importance: float = 1.0, sensitivity: float = 1.5):
        self.name = name
        self.reference = reference
        self.importance = importance
        self.sensitivity = sensitivity
    
    def to_dict(self):
        return {
            'default': self.reference,
            'weight': self.importance,
            'criticality': self.sensitivity
        }

cdef class AdaptiveFormula:
    """Core formula implementation - compiled and protected"""
    
    cdef dict config
    cdef str tier
    cdef object ml_model
    cdef double threshold
    cdef str license_key
    cdef list history
    cdef bint license_validated
    cdef double penalty_base
    
    def __init__(self, config: Dict, tier: str = 'community', license_key: str = None):
        self.config = config
        self.tier = tier
        self.license_key = license_key
        self.threshold = 0.65
        self.penalty_base = 0.02
        self.history = []
        self.license_validated = False
        
        # Validate license for premium tiers
        if tier != 'community':
            self.license_validated = self._validate_license()
            if not self.license_validated:
                print(f"Warning: Invalid license for {tier} tier. Falling back to community.")
                self.tier = 'community'
        
        self.ml_model = None if self.tier == 'community' else self._init_ml()
    
    cdef bint _validate_license(self):
        """Validate license key with expiration date"""
        if not self.license_key:
            return False
        
        from datetime import datetime
        
        # Format: PRO-YYYY-MM-DD-XXXX-XXXX or ENT-YYYY-MM-DD-XXXX-XXXX
        try:
            parts = self.license_key.split('-')
            if len(parts) < 6:
                return False
            
            tier_prefix = parts[0]
            year = int(parts[1])
            month = int(parts[2])
            day = int(parts[3])
            
            # Check tier match
            if self.tier == 'professional' and tier_prefix != 'PRO':
                return False
            elif self.tier == 'enterprise' and tier_prefix != 'ENT':
                return False
            
            # Check expiration
            expiry_date = datetime(year, month, day)
            today = datetime.now()
            
            if today > expiry_date:
                print(f"License expired on {expiry_date.date()}. Renew at licensing@adaptiveformula.ai")
                return False
            
            return True
            
        except (ValueError, IndexError):
            return False
    
    cdef double calculate_similarity(self, value, reference):
        """Protected similarity calculation"""
        cdef double sim
        
        if value is None:
            return 0.0
            
        if isinstance(value, (int, float)) and isinstance(reference, (int, float)):
            # Numerical similarity
            if fabs(<double>value) + fabs(<double>reference) < 1e-5:
                return 1.0
            sim = 1.0 - fabs(<double>value - <double>reference) / (fabs(<double>value) + fabs(<double>reference) + 1e-5)
            return max(0.0, min(1.0, sim))
        elif isinstance(value, str) and isinstance(reference, str):
            # String similarity
            return 1.0 if value == reference else 0.3
        elif isinstance(value, bool) and isinstance(reference, bool):
            # Boolean similarity
            return 1.0 if value == reference else 0.0
        else:
            # Default similarity for unknown types
            return 0.5
    
    cpdef double evaluate(self, dict data):
        """Main scoring function with adaptive learning"""
        cdef double numerator = 0.0
        cdef double denominator = 0.0
        cdef double score, weight, criticality, similarity
        cdef str field_name
        cdef dict field_config
        
        for field_name, field_config in self.config.items():
            value = data.get(field_name)
            reference = field_config.get('default')
            weight = <double>field_config.get('weight', 1.0)
            criticality = <double>field_config.get('criticality', 1.5)
            
            similarity = self.calculate_similarity(value, reference)
            
            # Apply ML optimization if available (Pro/Enterprise)
            if self.tier != 'community' and self.ml_model is not None:
                weight, criticality = self._optimize_params(field_name, similarity)
            
            numerator += similarity * weight * criticality
            denominator += weight * criticality
        
        score = numerator / denominator if denominator > 0 else 0.0
        
        # Apply penalty
        score *= (1.0 - self.penalty_base)
        
        # Adaptive learning for premium tiers
        if self.tier != 'community':
            self._update_history(score)
        
        return score
    
    cdef void _update_history(self, double score):
        """Update history and adapt threshold - Premium feature"""
        self.history.append(score)
        
        # Keep only last 100 evaluations
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        # Adaptive threshold adjustment after minimum history
        if len(self.history) > 10:
            recent_scores = self.history[-10:]
            avg_score = sum(recent_scores) / len(recent_scores)
            
            # Gradual threshold adjustment
            self.threshold = 0.65 + (avg_score - 0.5) * 0.1
            self.threshold = max(0.4, min(0.9, self.threshold))  # Keep in reasonable range
    
    cdef tuple _optimize_params(self, str field_name, double similarity):
        """ML optimization - Enterprise/Pro only"""
        # Phase 1: Basic adaptive optimization
        cdef double optimized_weight, optimized_criticality
        
        if self.tier == 'enterprise' and len(self.history) > 20:
            # More sophisticated for Enterprise
            history_avg = sum(self.history[-20:]) / 20.0
            optimized_weight = 2.0 + similarity * (1.0 + history_avg)
            optimized_criticality = 3.0 + (1.0 - similarity) * (1.0 + history_avg)
        else:
            # Basic optimization for Professional
            optimized_weight = 2.0 + similarity
            optimized_criticality = 3.0 + (1.0 - similarity)
        
        return (optimized_weight, optimized_criticality)
    
    cdef object _init_ml(self):
        """Initialize ML model for pro/enterprise tiers"""
        # Phase 1: Return placeholder, Phase 2: Real ML model
        return {'initialized': True, 'tier': self.tier}
    
    cpdef dict process_heterogeneous(self, data):
        """Handle heterogeneous data - Pro/Enterprise only"""
        if self.tier == 'community':
            if not isinstance(data, dict):
                raise ValueError("Community tier only supports dict data")
            return data
        
        # Complex heterogeneous handling
        return self._normalize_complex_data(data)
    
    cdef dict _normalize_complex_data(self, data):
        """Protected normalization logic"""
        cdef dict normalized = {}
        
        if isinstance(data, dict):
            return data
        
        # Handle pandas DataFrame - with improved error message
        if hasattr(data, '__class__') and data.__class__.__name__ == 'DataFrame':
            try:
                import pandas as pd
                if isinstance(data, pd.DataFrame):
                    return data.to_dict('records')[0] if len(data) > 0 else {}
            except ImportError:
                raise ImportError(
                    "DataFrame support requires pandas. Install it with: pip install pandas\n"
                    "Professional and Enterprise tiers support DataFrames, but pandas must be installed separately."
                )
        
        # Handle numpy arrays
        if isinstance(data, np.ndarray):
            return {'array_data': data.tolist()}
        
        # Handle nested structures
        if hasattr(data, '__dict__'):
            return vars(data)
        
        return {'data': data}
    
    cpdef double get_confidence_level(self):
        """Get current confidence level"""
        return self.threshold
    
    cpdef void set_confidence_level(self, double level):
        """Set confidence level manually"""
        self.threshold = max(0.0, min(1.0, level))
    
    cpdef dict get_metrics(self):
        """Get performance metrics - Premium feature"""
        if self.tier == 'community':
            return {'error': 'Metrics only available in Professional/Enterprise tiers'}
        
        if len(self.history) == 0:
            return {'evaluations': 0, 'avg_score': 0.0, 'current_threshold': self.threshold}
        
        return {
            'evaluations': len(self.history),
            'avg_score': sum(self.history) / len(self.history),
            'min_score': min(self.history),
            'max_score': max(self.history),
            'current_confidence_level': self.threshold,
            'tier': self.tier,
            'license_valid': self.license_validated
        }

# Wrapper class for easier Python usage
class CognitiveSDK:
    """Main SDK interface"""
    
    def __init__(self, tier: str = 'community', license_key: str = None):
        self.tier = tier
        self.license_key = license_key
        self.formula = None
        self.config = {}
    
    def configure(self, fields: List[Field]):
        """Configure fields for evaluation"""
        self.config = {field.name: field.to_dict() for field in fields}
        self.formula = AdaptiveFormula(self.config, self.tier, self.license_key)
    
    def evaluate(self, data: Dict) -> float:
        """Evaluate data against configured rules"""
        if not self.formula:
            raise RuntimeError("SDK not configured. Call configure() first.")
        
        if self.tier != 'community' and not isinstance(data, dict):
            data = self.formula.process_heterogeneous(data)
        
        return self.formula.evaluate(data)
    
    def set_confidence_level(self, level: float):
        """Set decision confidence level"""
        if self.formula:
            self.formula.set_confidence_level(level)
    
    def get_confidence_level(self) -> float:
        """Get current confidence level"""
        return self.formula.get_confidence_level() if self.formula else 0.65
    
    def get_metrics(self) -> Dict:
        """Get performance metrics (Premium only)"""
        if not self.formula:
            return {'error': 'SDK not configured'}
        return self.formula.get_metrics()