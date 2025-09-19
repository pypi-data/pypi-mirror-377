from pydantic import BaseModel

class MonitoringConfig(BaseModel):
    """Monitoring configuration."""
    
    enabled: bool = True
    metrics_enabled: bool = True
    health_enabled: bool = True
    discovery_port: int = 8001
    prometheus_enabled: bool = False

