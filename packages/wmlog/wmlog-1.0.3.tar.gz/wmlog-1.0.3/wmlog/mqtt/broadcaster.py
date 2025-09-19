"""
WML MQTT/WebSocket Broadcaster
=============================

Real-time log broadcasting system using MQTT and WebSocket protocols.
Extracted and enhanced from ProServe and EDPMT logging systems.
"""

import json
import asyncio
import logging
from typing import Set, Dict, Any, Optional, List, Union
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import threading
from queue import Queue, Empty

# MQTT support
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    mqtt = None

# WebSocket support  
try:
    from aiohttp import web, WSMsgType, ClientSession, ClientWebSocketResponse
    from aiohttp.web import WebSocketResponse
    import websockets
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    web = None
    WebSocketResponse = None
    websockets = None


@dataclass
class LogMessage:
    """Structured log message for broadcasting"""
    timestamp: str
    level: str
    service_name: str
    message: str
    logger_name: str
    thread_name: Optional[str] = None
    process_id: Optional[int] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    extra_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_data is None:
            self.extra_data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class WebSocketBroadcaster:
    """
    WebSocket-based log broadcaster for real-time log streaming
    Enhanced from EDPMT WebSocketLogBroadcaster
    """
    
    def __init__(self, max_history: int = 1000, port: int = 8080, path: str = "/ws/logs"):
        self.connections: Set[WebSocketResponse] = set()
        self.log_history: List[LogMessage] = []
        self.max_history = max_history
        self.port = port
        self.path = path
        self.broadcast_queue = asyncio.Queue()
        self._server_task: Optional[asyncio.Task] = None
        self._broadcast_task: Optional[asyncio.Task] = None
        self._running = False
        self._app = None
        self._runner = None
        
    async def start(self):
        """Start the WebSocket server"""
        if not WEBSOCKET_AVAILABLE:
            raise RuntimeError("WebSocket support not available - install aiohttp and websockets")
        
        if self._running:
            return
            
        # Create aiohttp application
        self._app = web.Application()
        self._app.router.add_get(self.path, self._websocket_handler)
        
        # Create runner
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        
        # Create site
        site = web.TCPSite(self._runner, 'localhost', self.port)
        await site.start()
        
        # Start broadcast task
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        self._running = True
        
        logging.info(f"WebSocket log broadcaster started on ws://localhost:{self.port}{self.path}")
    
    async def stop(self):
        """Stop the WebSocket server"""
        if not self._running:
            return
            
        self._running = False
        
        # Cancel broadcast task
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for ws in list(self.connections):
            await ws.close()
        self.connections.clear()
        
        # Cleanup runner
        if self._runner:
            await self._runner.cleanup()
        
        logging.info("WebSocket log broadcaster stopped")
    
    async def _websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        # Add connection
        self.connections.add(ws)
        logging.info(f"WebSocket client connected. Total connections: {len(self.connections)}")
        
        # Send recent log history
        await self._send_history_to_connection(ws)
        
        try:
            # Keep connection alive
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle client messages (ping, subscribe, etc.)
                    try:
                        data = json.loads(msg.data)
                        await self._handle_client_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({
                            "type": "error",
                            "message": "Invalid JSON format"
                        }))
                elif msg.type == WSMsgType.ERROR:
                    logging.error(f"WebSocket error: {ws.exception()}")
                    break
        except Exception as e:
            logging.error(f"WebSocket handler error: {e}")
        finally:
            # Remove connection
            self.connections.discard(ws)
            logging.info(f"WebSocket client disconnected. Total connections: {len(self.connections)}")
        
        return ws
    
    async def _send_history_to_connection(self, ws: WebSocketResponse):
        """Send recent log history to a new connection"""
        if not self.log_history:
            return
            
        try:
            history_message = {
                "type": "history",
                "logs": [log.to_dict() for log in self.log_history[-50:]]  # Last 50 logs
            }
            await ws.send_str(json.dumps(history_message))
        except Exception as e:
            logging.error(f"Error sending history to WebSocket client: {e}")
    
    async def _handle_client_message(self, ws: WebSocketResponse, data: Dict[str, Any]):
        """Handle messages from WebSocket clients"""
        msg_type = data.get("type")
        
        if msg_type == "ping":
            await ws.send_str(json.dumps({"type": "pong"}))
        elif msg_type == "subscribe":
            # Handle subscription filters (future enhancement)
            await ws.send_str(json.dumps({"type": "subscribed", "filters": data.get("filters", [])}))
        elif msg_type == "get_history":
            await self._send_history_to_connection(ws)
    
    async def _broadcast_loop(self):
        """Main broadcast loop"""
        while self._running:
            try:
                # Wait for log message
                log_message = await asyncio.wait_for(self.broadcast_queue.get(), timeout=1.0)
                
                # Add to history
                self.log_history.append(log_message)
                if len(self.log_history) > self.max_history:
                    self.log_history.pop(0)
                
                # Broadcast to all connections
                if self.connections:
                    broadcast_data = {
                        "type": "log",
                        "data": log_message.to_dict()
                    }
                    message = json.dumps(broadcast_data)
                    
                    # Send to all connected clients
                    disconnected = set()
                    for ws in list(self.connections):
                        try:
                            await ws.send_str(message)
                        except Exception as e:
                            logging.error(f"Error broadcasting to WebSocket client: {e}")
                            disconnected.add(ws)
                    
                    # Remove disconnected clients
                    self.connections -= disconnected
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logging.error(f"Broadcast loop error: {e}")
                await asyncio.sleep(1)
    
    async def broadcast_log(self, log_message: LogMessage):
        """Queue a log message for broadcasting"""
        try:
            await self.broadcast_queue.put(log_message)
        except Exception as e:
            logging.error(f"Error queueing log message: {e}")


class MQTTBroadcaster:
    """
    MQTT-based log broadcaster for distributed log streaming
    """
    
    def __init__(self, broker_host: str, broker_port: int = 1883, 
                 topic_prefix: str = "logs", qos: int = 1,
                 username: Optional[str] = None, password: Optional[str] = None):
        if not MQTT_AVAILABLE:
            raise RuntimeError("MQTT support not available - install paho-mqtt")
        
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic_prefix = topic_prefix
        self.qos = qos
        self.username = username
        self.password = password
        
        self.client: Optional[mqtt.Client] = None
        self._connected = False
        self._publish_queue = Queue()
        self._publish_thread: Optional[threading.Thread] = None
        self._running = False
    
    def start(self):
        """Start MQTT broadcaster"""
        if self._running:
            return
        
        # Create MQTT client
        self.client = mqtt.Client()
        
        # Set credentials if provided
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        try:
            # Connect to broker
            self.client.connect(self.broker_host, self.broker_port, 60)
            
            # Start network loop
            self.client.loop_start()
            
            # Start publish thread
            self._running = True
            self._publish_thread = threading.Thread(target=self._publish_loop, daemon=True)
            self._publish_thread.start()
            
            logging.info(f"MQTT broadcaster started: {self.broker_host}:{self.broker_port}")
            
        except Exception as e:
            logging.error(f"Failed to start MQTT broadcaster: {e}")
            raise
    
    def stop(self):
        """Stop MQTT broadcaster"""
        if not self._running:
            return
        
        self._running = False
        
        # Stop publish thread
        if self._publish_thread:
            self._publish_thread.join(timeout=5)
        
        # Disconnect MQTT client
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        
        logging.info("MQTT broadcaster stopped")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self._connected = True
            logging.info("MQTT broadcaster connected to broker")
        else:
            self._connected = False
            logging.error(f"MQTT broadcaster failed to connect: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self._connected = False
        logging.warning("MQTT broadcaster disconnected from broker")
    
    def _on_publish(self, client, userdata, mid):
        """MQTT publish callback"""
        # Optional: track published messages
        pass
    
    def _publish_loop(self):
        """Publishing thread loop"""
        while self._running:
            try:
                # Get message from queue
                log_message = self._publish_queue.get(timeout=1.0)
                
                if not self._connected:
                    logging.warning("MQTT not connected, dropping log message")
                    continue
                
                # Build topic
                topic = f"{self.topic_prefix}/{log_message.service_name}"
                
                # Publish message
                result = self.client.publish(topic, log_message.to_json(), qos=self.qos)
                
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    logging.error(f"MQTT publish failed: {result.rc}")
                
            except Empty:
                continue
            except Exception as e:
                logging.error(f"MQTT publish loop error: {e}")
    
    def broadcast_log(self, log_message: LogMessage):
        """Queue a log message for MQTT broadcasting"""
        try:
            self._publish_queue.put_nowait(log_message)
        except Exception as e:
            logging.error(f"Error queueing MQTT log message: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if MQTT client is connected"""
        return self._connected


class CombinedBroadcaster:
    """
    Combined WebSocket and MQTT broadcaster
    """
    
    def __init__(self, websocket_config: Optional[Dict[str, Any]] = None,
                 mqtt_config: Optional[Dict[str, Any]] = None):
        self.websocket_broadcaster = None
        self.mqtt_broadcaster = None
        
        if websocket_config:
            self.websocket_broadcaster = WebSocketBroadcaster(**websocket_config)
        
        if mqtt_config:
            self.mqtt_broadcaster = MQTTBroadcaster(**mqtt_config)
    
    async def start(self):
        """Start all broadcasters"""
        if self.websocket_broadcaster:
            await self.websocket_broadcaster.start()
        
        if self.mqtt_broadcaster:
            self.mqtt_broadcaster.start()
    
    async def stop(self):
        """Stop all broadcasters"""
        if self.websocket_broadcaster:
            await self.websocket_broadcaster.stop()
        
        if self.mqtt_broadcaster:
            self.mqtt_broadcaster.stop()
    
    async def broadcast_log(self, log_message: LogMessage):
        """Broadcast log to all configured broadcasters"""
        if self.websocket_broadcaster:
            await self.websocket_broadcaster.broadcast_log(log_message)
        
        if self.mqtt_broadcaster:
            self.mqtt_broadcaster.broadcast_log(log_message)
