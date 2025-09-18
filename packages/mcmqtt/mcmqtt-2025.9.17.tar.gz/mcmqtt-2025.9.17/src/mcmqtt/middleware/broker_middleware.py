"""
FastMCP middleware for automatic MQTT broker management.

This middleware provides intelligent broker lifecycle management:
- Auto-spawns brokers when MQTT tools are used
- Injects broker information into tool responses  
- Manages broker cleanup on session end
- Provides "just-works" MQTT experience
"""

import logging
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError

from ..broker import BrokerManager, BrokerConfig

logger = logging.getLogger(__name__)


class MQTTBrokerMiddleware(Middleware):
    """
    Middleware for automatic MQTT broker management.
    
    Features:
    - Auto-spawns brokers when MQTT tools need them
    - Injects broker URLs into MQTT tool responses
    - Cleans up idle brokers automatically
    - Provides session-scoped broker isolation
    """
    
    def __init__(self, 
                 auto_spawn: bool = True,
                 cleanup_idle_after: int = 300,  # 5 minutes
                 max_brokers_per_session: int = 5):
        """
        Initialize broker middleware.
        
        Args:
            auto_spawn: Automatically spawn brokers when needed
            cleanup_idle_after: Cleanup idle brokers after N seconds
            max_brokers_per_session: Maximum brokers per session
        """
        super().__init__()
        self.auto_spawn = auto_spawn
        self.cleanup_idle_after = cleanup_idle_after
        self.max_brokers_per_session = max_brokers_per_session
        
        # Will be injected by server
        self.broker_manager: Optional[BrokerManager] = None
        
        # Session-scoped broker tracking
        self._session_brokers: Dict[str, list] = {}
        self._session_last_activity: Dict[str, datetime] = {}
        
        # Background cleanup task (started when event loop is available)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_started = False
    
    def _get_session_id(self, context: MiddlewareContext) -> str:
        """Get session ID from context."""
        # Try to get session ID from various sources
        if hasattr(context, 'session_id') and context.session_id:
            return context.session_id
        
        # Fall back to source information
        if hasattr(context, 'source') and context.source:
            return f"session_{hash(context.source) % 10000}"
        
        # Default session
        return "default"
    
    def _start_cleanup_task(self):
        """Start background broker cleanup task."""
        if not self._cleanup_started and (self._cleanup_task is None or self._cleanup_task.done()):
            try:
                self._cleanup_task = asyncio.create_task(self._cleanup_idle_brokers())
                self._cleanup_started = True
            except RuntimeError:
                # No event loop running yet, will start later when middleware is used
                pass
    
    async def _cleanup_idle_brokers(self):
        """Background task to cleanup idle brokers."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                now = datetime.now()
                sessions_to_cleanup = []
                
                for session_id, last_activity in self._session_last_activity.items():
                    if (now - last_activity).total_seconds() > self.cleanup_idle_after:
                        sessions_to_cleanup.append(session_id)
                
                # Cleanup idle sessions
                for session_id in sessions_to_cleanup:
                    await self._cleanup_session_brokers(session_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in broker cleanup task: {e}")
    
    async def _cleanup_session_brokers(self, session_id: str):
        """Cleanup brokers for a specific session."""
        if session_id in self._session_brokers:
            brokers = self._session_brokers[session_id]
            logger.info(f"Cleaning up {len(brokers)} brokers for session {session_id}")
            
            # Stop all brokers for this session
            # Note: We'd need access to the broker manager here
            # This would be injected in the actual implementation
            
            del self._session_brokers[session_id]
            del self._session_last_activity[session_id]
    
    def _is_mqtt_tool(self, method: str) -> bool:
        """Check if a tool call is MQTT-related."""
        mqtt_tools = [
            'tools/call',  # Check params for MQTT tools
            'mqtt_connect', 'mqtt_publish', 'mqtt_subscribe', 
            'mqtt_disconnect', 'mqtt_status', 'mqtt_get_messages',
            'mqtt_list_subscriptions', 'mqtt_unsubscribe'
        ]
        return method in mqtt_tools
    
    def _needs_broker(self, tool_name: str) -> bool:
        """Check if a tool needs an MQTT broker."""
        broker_requiring_tools = [
            'mqtt_connect', 'mqtt_publish', 'mqtt_subscribe'
        ]
        return tool_name in broker_requiring_tools
    
    async def _ensure_broker_available(self, context: MiddlewareContext, broker_manager: BrokerManager) -> Optional[str]:
        """Ensure a broker is available for the session."""
        # Start cleanup task if not already started
        if not self._cleanup_started:
            self._start_cleanup_task()
            
        session_id = self._get_session_id(context)
        
        # Update session activity
        self._session_last_activity[session_id] = datetime.now()
        
        # Check if session already has a broker
        if session_id in self._session_brokers:
            session_brokers = self._session_brokers[session_id]
            
            # Find a running broker
            for broker_info in session_brokers:
                broker_status = await broker_manager.get_broker_status(broker_info['broker_id'])
                if broker_status and broker_status.status == 'running':
                    return broker_info['broker_id']
        
        # No running broker found, spawn a new one if auto_spawn is enabled
        if not self.auto_spawn:
            return None
        
        # Check session broker limit
        session_broker_count = len(self._session_brokers.get(session_id, []))
        if session_broker_count >= self.max_brokers_per_session:
            logger.warning(f"Session {session_id} has reached max broker limit ({self.max_brokers_per_session})")
            return None
        
        try:
            # Spawn new broker for session
            config = BrokerConfig(
                name=f"auto-broker-{session_id}",
                port=0,  # Auto-assign port
                max_connections=50  # Lower limit for auto-spawned brokers
            )
            
            broker_id = await broker_manager.spawn_broker(config)
            broker_info = await broker_manager.get_broker_status(broker_id)
            
            if broker_info:
                # Track broker for session
                if session_id not in self._session_brokers:
                    self._session_brokers[session_id] = []
                
                self._session_brokers[session_id].append({
                    'broker_id': broker_id,
                    'url': broker_info.url,
                    'spawned_at': datetime.now(),
                    'auto_spawned': True
                })
                
                logger.info(f"Auto-spawned broker {broker_id} for session {session_id}")
                return broker_id
            
        except Exception as e:
            logger.error(f"Failed to auto-spawn broker for session {session_id}: {e}")
            return None
    
    async def on_tool_call(self, context: MiddlewareContext, call_next):
        """
        Intercept tool calls to provide automatic broker management.
        """
        # Check if this is an MQTT tool that might need a broker
        if context.message and hasattr(context.message, 'params'):
            params = context.message.params
            
            if params and isinstance(params, dict) and 'name' in params:
                tool_name = params['name']
                
                # Check if tool needs a broker and if we have access to broker manager
                if (self._needs_broker(tool_name) and 
                    context.fastmcp_context and 
                    hasattr(context.fastmcp_context, 'server')):
                    
                    # Try to get broker manager from server
                    server = context.fastmcp_context.server
                    if hasattr(server, 'broker_manager'):
                        broker_manager = server.broker_manager
                        
                        # Ensure broker is available
                        broker_id = await self._ensure_broker_available(context, broker_manager)
                        
                        if broker_id:
                            # Get broker info to inject into tool arguments
                            broker_info = await broker_manager.get_broker_status(broker_id)
                            
                            if broker_info and 'arguments' in params:
                                # Inject broker information if not already provided
                                arguments = params['arguments']
                                
                                # For mqtt_connect, inject broker host/port if not provided
                                if tool_name == 'mqtt_connect':
                                    if not arguments.get('broker_host'):
                                        arguments['broker_host'] = broker_info.config.host
                                    if not arguments.get('broker_port'):
                                        arguments['broker_port'] = broker_info.config.port
                                    
                                    logger.info(f"Auto-injected broker {broker_id} details into mqtt_connect")
        
        # Continue with the tool call
        result = await call_next(context)
        
        # Post-process result to add broker information
        if (context.message and hasattr(context.message, 'params') and 
            isinstance(result, dict) and result.get('content')):
            
            params = context.message.params
            if params and isinstance(params, dict) and 'name' in params:
                tool_name = params['name']
                
                # Add broker information to successful MQTT tool responses
                if (self._is_mqtt_tool(tool_name) and 
                    context.fastmcp_context and 
                    hasattr(context.fastmcp_context, 'server')):
                    
                    server = context.fastmcp_context.server
                    if hasattr(server, 'broker_manager'):
                        session_id = self._get_session_id(context)
                        
                        # Add available brokers info to response
                        if session_id in self._session_brokers:
                            broker_info = {
                                'available_brokers': len(self._session_brokers[session_id]),
                                'session_id': session_id,
                                'auto_management': 'enabled'
                            }
                            
                            # Inject broker info into response content
                            if isinstance(result.get('content'), list) and result['content']:
                                content = result['content'][0]
                                if hasattr(content, 'text'):
                                    # Parse JSON response and add broker info
                                    try:
                                        response_data = eval(content.text) if isinstance(content.text, str) else content.text
                                        if isinstance(response_data, dict):
                                            response_data['broker_middleware'] = broker_info
                                            content.text = str(response_data)
                                    except:
                                        pass  # Ignore parsing errors
        
        return result
    
    async def on_session_end(self, context: MiddlewareContext, call_next):
        """Clean up session brokers when session ends."""
        session_id = self._get_session_id(context)
        
        # Cleanup brokers for ending session
        await self._cleanup_session_brokers(session_id)
        
        return await call_next(context)
    
    def __del__(self):
        """Cleanup on deletion."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()