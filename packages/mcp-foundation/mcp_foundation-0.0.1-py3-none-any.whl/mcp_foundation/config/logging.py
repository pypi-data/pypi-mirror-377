from pydantic import BaseModel
from typing import Optional

class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    enabled: bool = True
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_tool_calls: bool = True
    log_errors: bool = True
    log_dir: Optional[str] = None

