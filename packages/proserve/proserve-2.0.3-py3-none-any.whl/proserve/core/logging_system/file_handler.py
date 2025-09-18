"""
ProServe File Handler - Enhanced File Logging with Rotation and Buffering
Provides advanced file logging capabilities with rotation, buffering, and async support
"""

import os
import asyncio
import logging
import threading
from typing import List, Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import structlog

from .config import LoggingConfig


logger = structlog.get_logger(__name__)


class EnhancedFileHandler:
    """Enhanced file handler with rotation, buffering, and async support"""
    
    def __init__(self, config: LoggingConfig):
        self.config = config
        self.handler: Optional[logging.Handler] = None
        self.buffer: List[str] = []
        self.buffer_lock = threading.Lock()
        self.flush_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Setup the appropriate file handler
        if config.file_enabled:
            self.setup_handler()
    
    def setup_handler(self):
        """Setup appropriate file handler based on configuration"""
        if not self.config.file_path:
            logger.warning("File logging enabled but no file path specified")
            return
        
        # Ensure parent directory exists
        file_path = Path(self.config.file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if self.config.rotation_enabled:
                if self.config.rotation_type == 'size':
                    # Size-based rotation
                    max_bytes = self._parse_size(self.config.max_file_size)
                    self.handler = RotatingFileHandler(
                        filename=str(file_path),
                        maxBytes=max_bytes,
                        backupCount=self.config.backup_count,
                        encoding='utf-8'
                    )
                elif self.config.rotation_type == 'time':
                    # Time-based rotation
                    self.handler = TimedRotatingFileHandler(
                        filename=str(file_path),
                        when=self._parse_time_interval(self.config.rotation_interval),
                        backupCount=self.config.backup_count,
                        encoding='utf-8'
                    )
                else:
                    raise ValueError(f"Unknown rotation type: {self.config.rotation_type}")
            else:
                # No rotation
                self.handler = logging.FileHandler(
                    filename=str(file_path),
                    encoding='utf-8'
                )
            
            # Set logging level
            self.handler.setLevel(self.config.get_log_level_numeric(self.config.file_level))
            
            # Set formatter based on configuration
            formatter = self._create_formatter()
            self.handler.setFormatter(formatter)
            
            logger.info(f"File handler setup complete: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to setup file handler: {e}")
            self.handler = None
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        return self.config._parse_size(size_str)
    
    def _parse_time_interval(self, interval: str) -> str:
        """Parse time interval string for TimedRotatingFileHandler"""
        interval = interval.lower()
        
        # Map common intervals to handler format
        interval_map = {
            'midnight': 'midnight',
            'daily': 'D',
            'hourly': 'H',
            'weekly': 'W0',  # Monday
            'monthly': 'midnight'  # Closest approximation
        }
        
        return interval_map.get(interval, 'midnight')
    
    def _create_formatter(self) -> logging.Formatter:
        """Create appropriate formatter based on configuration"""
        if self.config.file_format == 'json':
            # JSON formatter
            return logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s", '
                '"module": "%(module)s", "funcName": "%(funcName)s", "lineno": %(lineno)d}'
            )
        elif self.config.file_format == 'structured':
            # Structured text formatter with more details
            return logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            # Simple text formatter
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
    
    async def start_async_logging(self):
        """Start async logging with buffering"""
        if not self.config.buffer_enabled or not self.handler:
            return
        
        self.is_running = True
        self.flush_task = asyncio.create_task(self._flush_buffer_periodically())
        logger.debug("Started async file logging with buffering")
    
    async def stop_async_logging(self):
        """Stop async logging and flush remaining buffer"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        
        # Flush any remaining logs
        self._flush_buffer()
        logger.debug("Stopped async file logging")
    
    async def _flush_buffer_periodically(self):
        """Periodically flush log buffer to file"""
        try:
            while self.is_running:
                await asyncio.sleep(self.config.flush_interval)
                self._flush_buffer()
        except asyncio.CancelledError:
            pass
        finally:
            # Final flush on shutdown
            self._flush_buffer()
    
    def _flush_buffer(self):
        """Flush buffered logs to file"""
        if not self.handler or not self.buffer:
            return
        
        with self.buffer_lock:
            if self.buffer:
                try:
                    for log_entry in self.buffer:
                        # Create a log record and emit it
                        record = logging.LogRecord(
                            name='proserve.buffered',
                            level=logging.INFO,
                            pathname='',
                            lineno=0,
                            msg=log_entry,
                            args=(),
                            exc_info=None
                        )
                        self.handler.emit(record)
                    
                    # Clear buffer after successful flush
                    flushed_count = len(self.buffer)
                    self.buffer.clear()
                    
                    if flushed_count > 0:
                        logger.debug(f"Flushed {flushed_count} log entries to file")
                        
                except Exception as e:
                    logger.error(f"Error flushing log buffer: {e}")
    
    def add_to_buffer(self, log_entry: str):
        """Add log entry to buffer"""
        if not self.config.buffer_enabled:
            return
        
        with self.buffer_lock:
            self.buffer.append(log_entry)
            
            # If buffer is full, force flush
            if len(self.buffer) >= self.config.buffer_size:
                self._flush_buffer()
    
    def log_direct(self, level: str, message: str, **kwargs):
        """Log message directly to file handler"""
        if not self.handler:
            return
        
        try:
            # Create log record
            numeric_level = getattr(logging, level.upper())
            record = logging.LogRecord(
                name='proserve.direct',
                level=numeric_level,
                pathname='',
                lineno=0,
                msg=message,
                args=(),
                exc_info=None
            )
            
            # Add extra fields
            for key, value in kwargs.items():
                setattr(record, key, value)
            
            self.handler.emit(record)
            
        except Exception as e:
            logger.error(f"Error logging directly to file: {e}")
    
    def rotate_log_file(self):
        """Manually trigger log rotation if supported"""
        if isinstance(self.handler, (RotatingFileHandler, TimedRotatingFileHandler)):
            try:
                if hasattr(self.handler, 'doRollover'):
                    self.handler.doRollover()
                    logger.info("Log file rotated manually")
            except Exception as e:
                logger.error(f"Error rotating log file: {e}")
        else:
            logger.warning("Manual log rotation not supported for current handler type")
    
    def get_log_file_info(self) -> dict:
        """Get information about the current log file"""
        if not self.handler or not self.config.file_path:
            return {}
        
        try:
            file_path = Path(self.config.file_path)
            info = {
                'path': str(file_path.absolute()),
                'exists': file_path.exists(),
                'readable': file_path.is_file() and os.access(file_path, os.R_OK),
                'writable': file_path.parent.exists() and os.access(file_path.parent, os.W_OK)
            }
            
            if file_path.exists():
                stat_info = file_path.stat()
                info.update({
                    'size_bytes': stat_info.st_size,
                    'modified_time': stat_info.st_mtime,
                    'created_time': stat_info.st_ctime
                })
            
            if isinstance(self.handler, RotatingFileHandler):
                info.update({
                    'rotation_type': 'size',
                    'max_bytes': self.handler.maxBytes,
                    'backup_count': self.handler.backupCount
                })
            elif isinstance(self.handler, TimedRotatingFileHandler):
                info.update({
                    'rotation_type': 'time',
                    'when': self.handler.when,
                    'backup_count': self.handler.backupCount
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting log file info: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Clean up file handler resources"""
        if self.handler:
            try:
                self.handler.flush()
                self.handler.close()
                logger.debug("File handler cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up file handler: {e}")
            finally:
                self.handler = None


class LogFileManager:
    """Manager for multiple log file handlers"""
    
    def __init__(self):
        self.handlers: dict[str, EnhancedFileHandler] = {}
    
    def add_handler(self, name: str, config: LoggingConfig) -> EnhancedFileHandler:
        """Add a new file handler"""
        handler = EnhancedFileHandler(config)
        self.handlers[name] = handler
        return handler
    
    def get_handler(self, name: str) -> Optional[EnhancedFileHandler]:
        """Get file handler by name"""
        return self.handlers.get(name)
    
    def remove_handler(self, name: str) -> bool:
        """Remove and cleanup file handler"""
        if name in self.handlers:
            handler = self.handlers.pop(name)
            handler.cleanup()
            return True
        return False
    
    async def start_all_async_logging(self):
        """Start async logging for all handlers"""
        for handler in self.handlers.values():
            await handler.start_async_logging()
    
    async def stop_all_async_logging(self):
        """Stop async logging for all handlers"""
        for handler in self.handlers.values():
            await handler.stop_async_logging()
    
    def cleanup_all(self):
        """Cleanup all file handlers"""
        for handler in self.handlers.values():
            handler.cleanup()
        self.handlers.clear()
    
    def get_all_file_info(self) -> dict:
        """Get information about all log files"""
        return {name: handler.get_log_file_info() 
                for name, handler in self.handlers.items()}
    
    def rotate_all_files(self):
        """Trigger rotation for all handlers that support it"""
        for name, handler in self.handlers.items():
            try:
                handler.rotate_log_file()
            except Exception as e:
                logger.error(f"Error rotating log file for handler '{name}': {e}")


# Global file manager instance
_file_manager: Optional[LogFileManager] = None


def get_file_manager() -> LogFileManager:
    """Get or create the global file manager"""
    global _file_manager
    if _file_manager is None:
        _file_manager = LogFileManager()
    return _file_manager


def create_file_handler(name: str, config: LoggingConfig) -> EnhancedFileHandler:
    """Create and register a new file handler"""
    manager = get_file_manager()
    return manager.add_handler(name, config)


def get_file_handler(name: str) -> Optional[EnhancedFileHandler]:
    """Get registered file handler by name"""
    manager = get_file_manager()
    return manager.get_handler(name)


async def start_async_file_logging():
    """Start async logging for all registered file handlers"""
    manager = get_file_manager()
    await manager.start_all_async_logging()


async def stop_async_file_logging():
    """Stop async logging for all registered file handlers"""
    manager = get_file_manager()
    await manager.stop_all_async_logging()


def cleanup_all_file_handlers():
    """Cleanup all file handlers"""
    manager = get_file_manager()
    manager.cleanup_all()
