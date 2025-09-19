"""
Adaptive Formula SDK - Cognitive Programming Infrastructure
Version 0.3.0 - Synchronized with core.pyx final API
"""

# Import from api.py which now matches core.pyx exactly
from .api import CognitiveSDK, Field

# Version info
__version__ = "0.3.0"

# Public API - matches README documentation
__all__ = ["CognitiveSDK", "Field"]

# Compatibility imports for previous versions (if needed)
try:
    from .models import FieldConfig, LicenseTier
    __all__.extend(["FieldConfig", "LicenseTier"])
except ImportError:
    # Models module not available, skip
    pass