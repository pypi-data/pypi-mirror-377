from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

class LicenseTier(Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

@dataclass
class FieldConfig:
    """Internal field configuration"""
    name: str
    default: Any
    weight: float = 1.0
    criticality: float = 1.5
    validator: Optional[callable] = None