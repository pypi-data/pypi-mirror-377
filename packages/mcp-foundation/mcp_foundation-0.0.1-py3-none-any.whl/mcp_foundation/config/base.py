
from typing import Optional, Union
from pydantic import BaseModel
from .server import ServerConfig
from .logging import LoggingConfig
from .monitoring import MonitoringConfig
from .security import SecurityConfig
from .cache import CacheConfig
from .event import EventConfig

class Settings(BaseModel):
	server: ServerConfig = ServerConfig()
	logging: LoggingConfig = LoggingConfig()
	monitoring: Optional[MonitoringConfig] = None
	security: Optional[SecurityConfig] = None
	cache: CacheConfig = CacheConfig()
	event: Optional[EventConfig] = None
	
	@classmethod
	def from_dict(cls, core_data: dict) -> 'Settings':
		foundation_dict = {}
		
		for field_name, field_info in cls.model_fields.items():
			config_class = field_info.annotation
			
			if hasattr(config_class, '__origin__') and config_class.__origin__ is Union:
				config_class = config_class.__args__[0]
			
			if not (isinstance(config_class, type) and issubclass(config_class, BaseModel)):
				continue
				
			config_fields = set(config_class.model_fields.keys())
			mapped_data = {k: v for k, v in core_data.items() if k in config_fields}
			
			if mapped_data:
				foundation_dict[field_name] = mapped_data
		
		return cls(**foundation_dict)
