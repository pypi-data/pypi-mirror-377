from pydantic import BaseModel
from typing import List

class EventConfig(BaseModel):
    """Event system configuration."""
    
    enabled: bool = False
    kafka_bootstrap_servers: List[str] = ["localhost:9092"]
    kafka_client_id: str = "mcp-server"
    topic_prefix: str = "mcp.server"
    enable_listener: bool = True
    enable_publisher: bool = True
    health_interval: int = 30
    metrics_interval: int = 60

