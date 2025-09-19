from pydantic import BaseModel
from typing import List

class SecurityConfig(BaseModel):
    """Security configuration."""
    
    enabled: bool = True
    dev_mode: bool = False
    auth_required: bool = False
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60
    api_keys: List[str] = []

