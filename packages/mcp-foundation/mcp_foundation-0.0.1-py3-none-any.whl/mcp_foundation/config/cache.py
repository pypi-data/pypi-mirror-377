from pydantic import BaseModel
from typing import Optional

class CacheConfig(BaseModel):
    """Cache configuration."""
    
    enabled: bool = True
    default_ttl: int = 300
    memory_max_size: int = 10000
    redis_url: Optional[str] = None
    key_prefix: str = "mcp:"
    enable_metrics: bool = True
    compress_large_values: bool = True
