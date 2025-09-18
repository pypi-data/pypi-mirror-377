"""
ProServe Log Broadcaster - WebSocket Log Broadcasting
Provides real-time log streaming to WebSocket clients for live monitoring
"""

import asyncio
import json
from typing import Set, List, Dict, Any, Optional
import structlog

# Optional WebSocket support
try:
    from aiohttp import web, WSMsgType
    from aiohttp.web import WebSocketResponse
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    web = None
    WSMsgType = None
    WebSocketResponse = None

from .config import LoggingConfig


logger = structlog.get_logger(__name__)


class LogBroadcaster:
    """WebSocket log broadcaster for real-time log streaming"""
    
    def __init__(self, config: Optional[LoggingConfig] = None):
        if not WEBSOCKET_AVAILABLE:
            logger.warning("WebSocket support not available - log broadcasting disabled")
            return
        
        self.config = config or LoggingConfig()
        self.connections: Set[WebSocketResponse] = set()
        self.log_buffer: List[Dict] = []
        self.max_buffer_size = self.config.websocket_buffer_size
        self.broadcaster_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Connection tracking
        self.connection_count = 0
        self.total_connections = 0
        self.messages_sent = 0
    
    async def add_connection(self, ws: WebSocketResponse):
        """Add WebSocket connection for log broadcasting"""
        if not WEBSOCKET_AVAILABLE:
            return
        
        self.connections.add(ws)
        self.connection_count += 1
        self.total_connections += 1
        
        logger.info(f"WebSocket log connection added. Active: {self.connection_count}")
        
        # Send buffered logs to new connection
        await self._send_buffered_logs(ws)
    
    async def remove_connection(self, ws: WebSocketResponse):
        """Remove WebSocket connection"""
        if not WEBSOCKET_AVAILABLE:
            return
        
        if ws in self.connections:
            self.connections.remove(ws)
            self.connection_count -= 1
            
            logger.info(f"WebSocket log connection removed. Active: {self.connection_count}")
    
    async def _send_buffered_logs(self, ws: WebSocketResponse):
        """Send buffered logs to a specific connection"""
        if not self.log_buffer:
            return
        
        try:
            # Send initial message with buffer info
            initial_msg = {
                'type': 'buffer_start',
                'count': len(self.log_buffer),
                'timestamp': asyncio.get_event_loop().time()
            }
            await ws.send_str(json.dumps(initial_msg))
            
            # Send buffered logs
            for log_entry in self.log_buffer:
                await ws.send_str(json.dumps(log_entry))
            
            # Send buffer end message
            end_msg = {
                'type': 'buffer_end',
                'timestamp': asyncio.get_event_loop().time()
            }
            await ws.send_str(json.dumps(end_msg))
            
        except Exception as e:
            logger.error(f"Error sending buffered logs to WebSocket: {e}")
            await self.remove_connection(ws)
    
    async def broadcast_log(self, log_entry: Dict):
        """Broadcast log entry to all connected WebSocket clients"""
        if not WEBSOCKET_AVAILABLE or not self.connections:
            return
        
        # Add to buffer
        self.log_buffer.append(log_entry)
        
        # Trim buffer if too large
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer = self.log_buffer[-self.max_buffer_size:]
        
        # Broadcast to all connections
        message = json.dumps(log_entry)
        disconnected_connections = set()
        
        for ws in self.connections.copy():  # Copy to avoid modification during iteration
            try:
                if ws.closed:
                    disconnected_connections.add(ws)
                else:
                    await ws.send_str(message)
                    self.messages_sent += 1
            except Exception as e:
                logger.debug(f"Error broadcasting to WebSocket: {e}")
                disconnected_connections.add(ws)
        
        # Clean up disconnected connections
        for ws in disconnected_connections:
            await self.remove_connection(ws)
    
    async def start_broadcaster(self):
        """Start the log broadcaster"""
        if not WEBSOCKET_AVAILABLE:
            logger.warning("Cannot start log broadcaster - WebSocket support not available")
            return
        
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Log broadcaster started")
    
    async def stop_broadcaster(self):
        """Stop the log broadcaster"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Close all connections
        for ws in self.connections.copy():
            try:
                if not ws.closed:
                    await ws.close()
            except Exception as e:
                logger.debug(f"Error closing WebSocket connection: {e}")
        
        self.connections.clear()
        self.connection_count = 0
        
        logger.info("Log broadcaster stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get broadcaster statistics"""
        return {
            'active_connections': self.connection_count,
            'total_connections': self.total_connections,
            'messages_sent': self.messages_sent,
            'buffer_size': len(self.log_buffer),
            'max_buffer_size': self.max_buffer_size,
            'is_running': self.is_running,
            'websocket_available': WEBSOCKET_AVAILABLE
        }
    
    def clear_buffer(self):
        """Clear the log buffer"""
        self.log_buffer.clear()
        logger.debug("Log buffer cleared")


class ProServeLogProcessor:
    """Custom log processor for ProServe with WebSocket broadcasting"""
    
    def __init__(self, broadcaster: Optional[LogBroadcaster] = None):
        self.broadcaster = broadcaster or get_log_broadcaster()
    
    def __call__(self, logger, method_name, event_dict):
        """Process log entry and broadcast if WebSocket broadcaster available"""
        # Create structured log entry for broadcasting
        log_entry = {
            'timestamp': event_dict.get('timestamp'),
            'level': method_name.upper(),
            'logger': str(logger.name) if hasattr(logger, 'name') else 'unknown',
            'message': event_dict.get('event', ''),
            'context': {k: v for k, v in event_dict.items() 
                       if k not in ['timestamp', 'event', 'level']},
            'type': 'log'
        }
        
        # Broadcast to WebSocket clients
        if self.broadcaster and WEBSOCKET_AVAILABLE:
            asyncio.create_task(self.broadcaster.broadcast_log(log_entry))
        
        return event_dict


async def websocket_log_handler(request):
    """WebSocket handler for log streaming"""
    if not WEBSOCKET_AVAILABLE:
        return web.Response(text="WebSocket support not available", status=503)
    
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    broadcaster = get_log_broadcaster()
    await broadcaster.add_connection(ws)
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    # Handle client messages (e.g., filter requests)
                    await handle_websocket_message(ws, data, broadcaster)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from WebSocket client: {msg.data}")
            elif msg.type == WSMsgType.ERROR:
                logger.error(f"WebSocket error: {ws.exception()}")
                break
    except Exception as e:
        logger.error(f"WebSocket handler error: {e}")
    finally:
        await broadcaster.remove_connection(ws)
    
    return ws


async def handle_websocket_message(ws: WebSocketResponse, data: Dict[str, Any], 
                                 broadcaster: LogBroadcaster):
    """Handle messages from WebSocket clients"""
    message_type = data.get('type')
    
    if message_type == 'ping':
        # Respond to ping
        await ws.send_str(json.dumps({
            'type': 'pong',
            'timestamp': asyncio.get_event_loop().time()
        }))
    
    elif message_type == 'get_stats':
        # Send broadcaster statistics
        stats = broadcaster.get_stats()
        await ws.send_str(json.dumps({
            'type': 'stats',
            'data': stats
        }))
    
    elif message_type == 'clear_buffer':
        # Clear log buffer (admin action)
        broadcaster.clear_buffer()
        await ws.send_str(json.dumps({
            'type': 'buffer_cleared',
            'timestamp': asyncio.get_event_loop().time()
        }))
    
    elif message_type == 'set_filter':
        # Set log filtering (future enhancement)
        logger.debug(f"Filter request from WebSocket client: {data}")
        # TODO: Implement per-connection filtering
    
    else:
        logger.warning(f"Unknown WebSocket message type: {message_type}")


def setup_log_endpoints(app, websocket_path: str = "/logs"):
    """Setup WebSocket endpoints for log streaming"""
    if not WEBSOCKET_AVAILABLE:
        logger.warning("Cannot setup log endpoints - WebSocket support not available")
        return
    
    # Add WebSocket route for log streaming
    app.router.add_get(websocket_path, websocket_log_handler)
    
    # Add HTTP endpoint for log information
    async def log_info_handler(request):
        broadcaster = get_log_broadcaster()
        stats = broadcaster.get_stats()
        return web.json_response(stats)
    
    app.router.add_get(f"{websocket_path}/info", log_info_handler)
    
    # Add endpoint to get recent logs as JSON
    async def recent_logs_handler(request):
        broadcaster = get_log_broadcaster()
        limit = int(request.query.get('limit', 100))
        
        recent_logs = broadcaster.log_buffer[-limit:] if broadcaster.log_buffer else []
        
        return web.json_response({
            'logs': recent_logs,
            'total': len(recent_logs),
            'buffer_size': len(broadcaster.log_buffer)
        })
    
    app.router.add_get(f"{websocket_path}/recent", recent_logs_handler)
    
    logger.info(f"Log endpoints setup: {websocket_path}")


# Global log broadcaster instance
_log_broadcaster: Optional[LogBroadcaster] = None


def get_log_broadcaster(config: Optional[LoggingConfig] = None) -> LogBroadcaster:
    """Get the global log broadcaster instance"""
    global _log_broadcaster
    if _log_broadcaster is None:
        _log_broadcaster = LogBroadcaster(config)
    return _log_broadcaster


def reset_log_broadcaster():
    """Reset the global log broadcaster instance"""
    global _log_broadcaster
    if _log_broadcaster:
        asyncio.create_task(_log_broadcaster.stop_broadcaster())
    _log_broadcaster = None


async def start_log_broadcasting(config: Optional[LoggingConfig] = None):
    """Start log broadcasting with optional configuration"""
    broadcaster = get_log_broadcaster(config)
    await broadcaster.start_broadcaster()


async def stop_log_broadcasting():
    """Stop log broadcasting"""
    broadcaster = get_log_broadcaster()
    await broadcaster.stop_broadcaster()


def create_log_processor(broadcaster: Optional[LogBroadcaster] = None) -> ProServeLogProcessor:
    """Create a log processor with WebSocket broadcasting"""
    return ProServeLogProcessor(broadcaster)


# Utility functions for WebSocket log streaming
def is_websocket_available() -> bool:
    """Check if WebSocket support is available"""
    return WEBSOCKET_AVAILABLE


def get_broadcaster_stats() -> Dict[str, Any]:
    """Get statistics from the global broadcaster"""
    broadcaster = get_log_broadcaster()
    return broadcaster.get_stats()
