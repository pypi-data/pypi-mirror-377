"""
ProServe Background Task Manager - Background Task Execution and Management
Handles periodic tasks, scheduled jobs, and background script execution
"""

import asyncio
import importlib
import importlib.util
import os
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
import structlog


class BackgroundTaskManager:
    """Manages background tasks and scheduled jobs for ProServe services"""
    
    def __init__(self, service_core, manifest):
        """Initialize background task manager"""
        self.service_core = service_core
        self.manifest = manifest
        self.logger = service_core.get_logger()
        
        # Task tracking
        self.task_handles: List[asyncio.Task] = []
        self.task_registry: Dict[str, Dict[str, Any]] = {}
        
    async def setup_background_tasks(self):
        """Setup and start all background tasks from manifest"""
        if not hasattr(self.manifest, 'background_tasks') or not self.manifest.background_tasks:
            return
        
        for task_spec in self.manifest.background_tasks:
            try:
                await self._setup_single_task(task_spec)
            except Exception as e:
                task_name = task_spec.get('name', 'unnamed_task')
                self.logger.error(f"Failed to start background task {task_name}: {e}")
    
    async def _setup_single_task(self, task_spec: Dict[str, Any]):
        """Setup and start a single background task"""
        task_name = task_spec.get('name', 'unnamed_task')
        handler = task_spec.get('handler')
        script = task_spec.get('script')
        interval = task_spec.get('interval', 60)  # Default 60 seconds
        broadcast = task_spec.get('broadcast', False)
        
        # Create task function
        if script:
            task_func = self._load_script_for_task(script, task_spec)
        elif handler:
            task_func = self._load_handler_for_task(handler)
        else:
            raise ValueError(f"Task {task_name} must specify either 'script' or 'handler'")
        
        # Create and start the periodic task
        task = asyncio.create_task(
            self._run_periodic_task(task_func, interval, task_name, broadcast)
        )
        
        # Track the task
        self.task_handles.append(task)
        self.task_registry[task_name] = {
            'config': task_spec,
            'task': task,
            'function': task_func,
            'interval': interval,
            'broadcast': broadcast
        }
        
        self.logger.info(f"Started background task: {task_name} (interval: {interval}s)")
    
    async def _run_periodic_task(self, task_func: Callable, interval: int, 
                                task_name: str, broadcast: bool = False):
        """Run a task periodically with error handling"""
        while True:
            try:
                self.logger.debug(f"Executing background task: {task_name}")
                
                # Execute the task
                result = await task_func()
                
                # Broadcast result if requested
                if broadcast and result:
                    await self._broadcast_task_result(task_name, result)
                
                self.logger.debug(f"Background task completed: {task_name}")
                
            except asyncio.CancelledError:
                self.logger.info(f"Background task cancelled: {task_name}")
                break
            except Exception as e:
                self.logger.error(f"Background task error in {task_name}: {e}")
                # Continue running even if task fails
            
            # Wait for the next execution
            try:
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                self.logger.info(f"Background task sleep cancelled: {task_name}")
                break
    
    def _load_script_for_task(self, script_path: str, task_config: Dict[str, Any]) -> Callable:
        """Load and prepare a Python script for background task execution"""
        # Convert relative path to absolute
        if not os.path.isabs(script_path):
            if hasattr(self.manifest, '_manifest_path'):
                manifest_dir = Path(self.manifest._manifest_path).parent
                project_root = manifest_dir.parent
                script_path = str(project_root / script_path)
            else:
                script_path = str(Path.cwd() / script_path)
        
        if not Path(script_path).exists():
            raise FileNotFoundError(f"Background task script not found: {script_path}")
        
        # Load the script
        spec = importlib.util.spec_from_file_location("bg_task_script", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the main function
        if hasattr(module, 'main'):
            script_main = module.main
        elif hasattr(module, 'execute'):
            script_main = module.execute
        elif hasattr(module, 'run'):
            script_main = module.run
        else:
            raise AttributeError(f"Background task script {script_path} must have 'main', 'execute', or 'run' function")
        
        # Create wrapper with isolation support
        async def bg_script_wrapper():
            try:
                # Check if isolation is required
                isolation_config = task_config.get('isolation', self.manifest.isolation)
                
                if isolation_config.get('mode', 'none') != 'none':
                    # Execute with isolation
                    result = await self.service_core.isolation_manager.execute_script(
                        script_path=script_path,
                        service=self.service_core,
                        script_context={'task_config': task_config}
                    )
                else:
                    # Execute directly
                    if asyncio.iscoroutinefunction(script_main):
                        result = await script_main()
                    else:
                        result = script_main()
                
                return result
                
            except Exception as e:
                task_name = task_config.get('name', 'unnamed_task')
                self.logger.error(f"Background task execution failed: {e}", 
                                script=str(script_path), task=task_name)
                raise
        
        return bg_script_wrapper
    
    def _load_handler_for_task(self, handler_path: str) -> Callable:
        """Load handler function for background task"""
        try:
            module_path, func_name = handler_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            handler_func = getattr(module, func_name)
            
            # Wrap synchronous functions to be async
            if not asyncio.iscoroutinefunction(handler_func):
                async def async_wrapper():
                    return handler_func()
                return async_wrapper
            
            return handler_func
            
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Cannot load background task handler {handler_path}: {e}")
    
    async def _broadcast_task_result(self, task_name: str, result: Any):
        """Broadcast task result to WebSocket connections"""
        if not self.service_core.websocket_connections:
            return
        
        message = {
            'type': 'background_task_result',
            'task': task_name,
            'result': result,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        # Send to all connected WebSocket clients
        disconnected = set()
        for ws in self.service_core.websocket_connections:
            try:
                await ws.send_str(json.dumps(message))
            except Exception as e:
                self.logger.warning(f"Failed to broadcast to WebSocket: {e}")
                disconnected.add(ws)
        
        # Remove disconnected WebSockets
        self.service_core.websocket_connections -= disconnected
    
    async def stop_all_tasks(self):
        """Stop all background tasks gracefully"""
        self.logger.info("Stopping all background tasks...")
        
        for task in self.task_handles:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete cancellation
        if self.task_handles:
            await asyncio.gather(*self.task_handles, return_exceptions=True)
        
        self.task_handles.clear()
        self.task_registry.clear()
        
        self.logger.info("All background tasks stopped")
    
    async def add_task(self, task_spec: Dict[str, Any]) -> str:
        """Add a new background task at runtime"""
        task_name = task_spec.get('name')
        if not task_name:
            raise ValueError("Task specification must include 'name'")
        
        if task_name in self.task_registry:
            raise ValueError(f"Task {task_name} already exists")
        
        await self._setup_single_task(task_spec)
        return task_name
    
    async def remove_task(self, task_name: str):
        """Remove a background task by name"""
        if task_name not in self.task_registry:
            raise ValueError(f"Task {task_name} not found")
        
        task_info = self.task_registry[task_name]
        task = task_info['task']
        
        # Cancel the task
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Remove from tracking
        self.task_handles.remove(task)
        del self.task_registry[task_name]
        
        self.logger.info(f"Removed background task: {task_name}")
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all background tasks"""
        status = {
            'total_tasks': len(self.task_registry),
            'active_tasks': sum(1 for task in self.task_handles if not task.done()),
            'tasks': {}
        }
        
        for task_name, task_info in self.task_registry.items():
            task = task_info['task']
            status['tasks'][task_name] = {
                'interval': task_info['interval'],
                'broadcast': task_info['broadcast'],
                'running': not task.done(),
                'cancelled': task.cancelled() if hasattr(task, 'cancelled') else False
            }
        
        return status
    
    async def execute_task_once(self, task_name: str) -> Any:
        """Execute a specific task once (outside of its normal schedule)"""
        if task_name not in self.task_registry:
            raise ValueError(f"Task {task_name} not found")
        
        task_info = self.task_registry[task_name]
        task_func = task_info['function']
        
        self.logger.info(f"Executing task once: {task_name}")
        
        try:
            result = await task_func()
            self.logger.info(f"One-time task execution completed: {task_name}")
            return result
        except Exception as e:
            self.logger.error(f"One-time task execution failed: {task_name}: {e}")
            raise
