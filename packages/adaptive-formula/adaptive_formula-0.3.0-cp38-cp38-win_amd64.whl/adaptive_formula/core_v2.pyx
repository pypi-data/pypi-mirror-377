# cython: language_level=3
# distutils: language=c++

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
cimport numpy as np
from libc.math cimport fabs

cdef class AdaptiveFormula:
    """Core formula implementation - compiled and protected"""
    
    cdef dict config
    cdef str tier
    cdef object ml_model
    cdef double threshold
    
    def __init__(self, config: Dict, tier: str = 'community'):
        self.config = config
        self.tier = tier
        self.threshold = 0.65
        self.ml_model = None if tier == 'community' else self._init_ml()
    
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
        """Main scoring function - protected implementation"""
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
            
            # Apply ML optimization if available
            if self.tier != 'community' and self.ml_model is not None:
                weight, criticality = self._optimize_params(field_name, similarity)
            
            numerator += similarity * weight * criticality
            denominator += weight * criticality
        
        return numerator / denominator if denominator > 0 else 0.0
    
    cdef tuple _optimize_params(self, str field_name, double similarity):
        """ML optimization - Enterprise only"""
        # Simulated ML optimization
        # In production, this would use actual ML model
        cdef double optimized_weight = 2.0 + similarity
        cdef double optimized_criticality = 3.0 + (1.0 - similarity)
        return (optimized_weight, optimized_criticality)
    
    cdef object _init_ml(self):
        """Initialize ML model for pro/enterprise tiers"""
        # Placeholder for ML model initialization
        return None
    
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
        
        # Handle pandas DataFrame
        try:
            import pandas as pd
            if isinstance(data, pd.DataFrame):
                return data.to_dict('records')[0] if len(data) > 0 else {}
        except ImportError:
            pass
        
        # Handle numpy arrays
        if isinstance(data, np.ndarray):
            return {'array_data': data.tolist()}
        
        # Handle nested structures
        if hasattr(data, '__dict__'):
            return vars(data)
        
        return {'data': data}
    
    cpdef double get_threshold(self):
        """Get current threshold"""
        return self.threshold
    
    cpdef void set_threshold(self, double threshold):
        """Set threshold"""
        self.threshold = max(0.0, min(1.0, threshold))