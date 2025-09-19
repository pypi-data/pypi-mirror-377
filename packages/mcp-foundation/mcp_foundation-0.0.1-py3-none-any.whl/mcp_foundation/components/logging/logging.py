import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from ..base_component import BaseComponent

logger = logging.getLogger(__name__)


class SimpleFormatter(logging.Formatter):
    """Simple, clean formatter for MCP Foundation logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with clean structure."""
        # Add component name from logger name
        parts = record.name.split('.')
        if len(parts) >= 2:
            # Extract meaningful component name
            component = parts[-2] if parts[-1] in ['logging', 'cache', 'server'] else parts[-1]
        else:
            component = record.name
        
        record.component = component[:12]  # Limit length
        
        # Use clean format
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-5s | %(component)-12s | %(message)s",
            datefmt="%H:%M:%S"
        )
        
        return formatter.format(record)


class LogManager:
    """Simple logging manager for MCP Foundation."""
    
    def __init__(self, config):
        self.config = config
        self.loggers = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup the root logger for MCP Foundation."""
        # Get or create root logger
        root_logger = logging.getLogger('mcp_foundation')
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Set level
        level = getattr(logging, self.config.level.upper(), logging.INFO)
        root_logger.setLevel(level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Set formatter
        formatter = SimpleFormatter()
        console_handler.setFormatter(formatter)
        
        root_logger.addHandler(console_handler)
        
        # Add file handler if log_dir is specified
        if self.config.log_dir:
            self._add_file_handler(root_logger, level, formatter)
        
        # Prevent propagation to avoid duplicate logs
        root_logger.propagate = False
        
        self.root_logger = root_logger
        logger.info(f"Logging initialized - Level: {self.config.level.upper()}")
    
    def _add_file_handler(self, root_logger, level, formatter):
        """Add file handler if log directory is configured."""
        try:
            log_dir = Path(self.config.log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / "mcp_foundation.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            logger.info(f"File logging enabled: {log_file}")
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance."""
        if not name.startswith('mcp_foundation'):
            name = f'mcp_foundation.{name}'
        
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        
        return self.loggers[name]
    
    def set_level(self, level: str):
        """Change log level dynamically."""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.root_logger.setLevel(numeric_level)
        
        # Update all handlers
        for handler in self.root_logger.handlers:
            handler.setLevel(numeric_level)
        
        self.config.level = level
        logger.info(f"Log level changed to {level.upper()}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        return {
            "level": self.config.level,
            "handlers": len(self.root_logger.handlers),
            "file_logging": bool(self.config.log_dir),
            "log_tool_calls": self.config.log_tool_calls,
            "loggers_count": len(self.loggers)
        }


# Global log manager instance
_log_manager: Optional[LogManager] = None


def get_log_manager() -> Optional[LogManager]:
    """Get the global log manager instance."""
    return _log_manager


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance. Falls back to standard logging if manager not initialized."""
    global _log_manager
    
    if _log_manager:
        return _log_manager.get_logger(name or __name__)
    else:
        # Fallback to standard logging
        return logging.getLogger(name or __name__)


class LoggingComponent(BaseComponent):
    name = "logging"

    def register(self, server, config=None):
        """Register logging component with the server."""
        if not config or not config.logging or not config.logging.enabled:
            logger.info("Logging component: using default configuration")
            return
        
        # Initialize log manager with config
        global _log_manager
        _log_manager = LogManager(config.logging)
        
        # Add logging utilities to server if supported
        if hasattr(server, '_log_manager'):
            server._log_manager = _log_manager
        
        logger.info(f"✅ Logging component registered - Level: {config.logging.level}, File: {'Yes' if config.logging.log_dir else 'No'}")
