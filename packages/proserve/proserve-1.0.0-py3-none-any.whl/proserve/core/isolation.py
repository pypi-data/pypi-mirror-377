"""
ProServe Process Isolation Framework
Manages process isolation and virtualization for script execution with multi-environment support
"""

import asyncio
import json
import os
import sys
import tempfile
import base64
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, Union

# ProServe logging imports
try:
    from .logging import setup_logging, create_logger
    PROSERVE_LOGGING_AVAILABLE = True
except ImportError:
    PROSERVE_LOGGING_AVAILABLE = False
    def setup_logging(**kwargs):
        import structlog
        return structlog.get_logger()

# Extended isolation environments
try:
    from ..isolation.extended_environments import (
        MicroPythonIsolationManager,
        ArduinoIsolationManager,
        create_extended_isolation_manager
    )
    EXTENDED_ENVIRONMENTS_AVAILABLE = True
except ImportError:
    EXTENDED_ENVIRONMENTS_AVAILABLE = False
    MicroPythonIsolationManager = None
    ArduinoIsolationManager = None

# Docker isolation imports (optional)
try:
    from ..docker.isolation import DockerIsolationManager
    DOCKER_ISOLATION_AVAILABLE = True
except ImportError:
    DOCKER_ISOLATION_AVAILABLE = False
    DockerIsolationManager = None


class MockRequest:
    """Mock request object for subprocess execution"""
    def __init__(self, data):
        if data:
            self.method = data.get('method', 'GET')
            self.path = data.get('path', '/')
            self.query_string = data.get('query_string', '')
            self.headers = data.get('headers', {})
            self.content_type = data.get('content_type', 'application/json')
            self._body = data.get('body')
            self._body_is_base64 = data.get('body_is_base64', False)
        else:
            self.method = 'GET'
            self.path = '/'
            self.query_string = ''
            self.headers = {}
            self.content_type = 'application/json'
            self._body = None
            self._body_is_base64 = False
    
    async def json(self):
        if self._body:
            if self._body_is_base64:
                body = base64.b64decode(self._body).decode('utf-8')
            else:
                body = self._body
            return json.loads(body) if isinstance(body, str) else body
        return {}
    
    async def text(self):
        if self._body:
            if self._body_is_base64:
                return base64.b64decode(self._body).decode('utf-8')
            return self._body
        return ""
    
    async def read(self):
        if self._body:
            if self._body_is_base64:
                return base64.b64decode(self._body)
            return self._body.encode('utf-8') if isinstance(self._body, str) else self._body
        return b""


class MockResponse:
    """Mock response class for subprocess execution"""
    def __init__(self, data=None, status=200, headers=None):
        self.data = data
        self.status = status
        self.headers = headers or {}
    
    def to_dict(self):
        return {
            'data': self.data,
            'status': self.status,
            'headers': self.headers
        }


class MockLogger:
    """Mock logger for subprocess execution"""
    def info(self, msg, **kwargs):
        print(f"[INFO] {msg} {kwargs}")
    
    def error(self, msg, **kwargs):
        print(f"[ERROR] {msg} {kwargs}")
    
    def warning(self, msg, **kwargs):
        print(f"[WARNING] {msg} {kwargs}")
    
    def debug(self, msg, **kwargs):
        print(f"[DEBUG] {msg} {kwargs}")


class MockService:
    """Mock service object for subprocess execution"""
    def __init__(self, service_name="proserve-subprocess"):
        self.logger = MockLogger()
        self.name = service_name
        self.proserve_client = None  # Changed from edpmt_client
        self.websocket_connections = set()
    
    def __getattr__(self, name):
        # Return None for any other attributes
        return None


class ProcessIsolationManager:
    """Manages process isolation and virtualization for script execution with multi-environment support"""
    
    def __init__(self, isolation_config: Dict[str, Any]):
        self.config = isolation_config
        self.mode = isolation_config.get('mode', 'none')
        self.timeout = isolation_config.get('timeout', 30)
        self.memory_limit = isolation_config.get('memory_limit')
        self.cpu_limit = isolation_config.get('cpu_limit')
        self.network_isolation = isolation_config.get('network_isolation', False)
        self.filesystem_isolation = isolation_config.get('filesystem_isolation', False)
        self.environment_isolation = isolation_config.get('environment_isolation', True)
        self.auto_environment = isolation_config.get('auto_environment', True)
        self.force_environment = isolation_config.get('force_environment', None)
        self.platform = isolation_config.get('platform')
        self.board = isolation_config.get('board')
        
        # Initialize extended isolation managers
        self.micropython_manager = None
        self.arduino_manager = None
        self.docker_manager = None
        
        # Initialize extended environments if available
        if EXTENDED_ENVIRONMENTS_AVAILABLE:
            if self.mode == 'micropython' or self.platform in ['rp2040', 'esp32', 'esp8266']:
                try:
                    self.micropython_manager = create_extended_isolation_manager(
                        'micropython', isolation_config
                    )
                    print("🐍 MicroPython isolation manager initialized")
                except Exception as e:
                    print(f"⚠️  Failed to initialize MicroPython manager: {e}")
            
            elif self.mode == 'arduino' or self.platform in ['arduino_uno', 'arduino_nano']:
                try:
                    self.arduino_manager = create_extended_isolation_manager(
                        'arduino', isolation_config
                    )
                    print("🤖 Arduino isolation manager initialized")
                except Exception as e:
                    print(f"⚠️  Failed to initialize Arduino manager: {e}")
        
        # Initialize Docker isolation manager if available and needed
        if DOCKER_ISOLATION_AVAILABLE and self.mode in ['docker', 'container']:
            try:
                self.docker_manager = DockerIsolationManager(isolation_config)
                print("🐳 Docker isolation manager initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize Docker isolation manager: {e}")
                self.docker_manager = None
    
    async def execute_script(self, script_path: str, service, request_data: Any = None, script_context = None) -> Any:
        """Execute script with configured isolation mode and enhanced logging context"""
        
        # Extended environment execution
        if self.mode == 'micropython' and self.micropython_manager:
            return await self._execute_micropython(script_path, service, request_data, script_context)
        elif self.mode == 'arduino' and self.arduino_manager:
            return await self._execute_arduino(script_path, service, request_data, script_context)
        
        # Standard execution modes
        if self.mode == 'none':
            return await self._execute_direct(script_path, service, request_data, script_context)
        elif self.mode == 'process':
            return await self._execute_subprocess(script_path, service, request_data, script_context)
        elif self.mode == 'docker' or (self.mode == 'container' and self.docker_manager):
            return await self._execute_docker(script_path, service, request_data, script_context)
        elif self.mode == 'container':
            return await self._execute_container(script_path, service, request_data, script_context)
        elif self.mode == 'sandbox':
            return await self._execute_sandbox(script_path, service, request_data, script_context)
        else:
            raise ValueError(f"Unknown isolation mode: {self.mode}")
    
    async def _execute_micropython(self, script_path: str, service, request_data: Any, script_context = None) -> Any:
        """Execute script on MicroPython platform"""
        if not self.micropython_manager:
            service.logger.error("❌ MicroPython isolation manager not available")
            raise RuntimeError("MicroPython isolation not available")
        
        try:
            service.logger.info(f"🐍 Executing script on MicroPython: {script_path}")
            
            # Execute script using MicroPython isolation manager
            result = await self.micropython_manager.execute_script(
                script_path=script_path,
                service=service,
                request_data=request_data,
                script_context=script_context
            )
            
            service.logger.info(f"✅ MicroPython execution successful")
            return result
            
        except Exception as e:
            service.logger.error(f"❌ MicroPython execution failed: {e}")
            
            # Fallback to subprocess if configured
            if self.config.get('fallback_on_platform_failure', True):
                service.logger.warning("⚠️  Falling back to subprocess isolation")
                return await self._execute_subprocess(script_path, service, request_data, script_context)
            else:
                raise
    
    async def _execute_arduino(self, script_path: str, service, request_data: Any, script_context = None) -> Any:
        """Execute script on Arduino platform"""
        if not self.arduino_manager:
            service.logger.error("❌ Arduino isolation manager not available")
            raise RuntimeError("Arduino isolation not available")
        
        try:
            service.logger.info(f"🤖 Executing script on Arduino: {script_path}")
            
            # Execute script using Arduino isolation manager
            result = await self.arduino_manager.execute_script(
                script_path=script_path,
                service=service,
                request_data=request_data,
                script_context=script_context
            )
            
            service.logger.info(f"✅ Arduino execution successful")
            return result
            
        except Exception as e:
            service.logger.error(f"❌ Arduino execution failed: {e}")
            
            # Fallback to subprocess if configured
            if self.config.get('fallback_on_platform_failure', True):
                service.logger.warning("⚠️  Falling back to subprocess isolation")
                return await self._execute_subprocess(script_path, service, request_data, script_context)
            else:
                raise
    
    async def _execute_direct(self, script_path: str, service, request_data: Any, script_context = None) -> Any:
        """Execute script directly in current process (no isolation)"""
        return await self._load_and_execute_script(script_path, service, request_data, script_context)
    
    async def _execute_subprocess(self, script_path: str, service, request_data: Any, script_context = None) -> Any:
        """Execute script in separate subprocess for process isolation"""
        # Prepare execution environment
        env = os.environ.copy() if not self.environment_isolation else {}
        
        # Serialize request data for subprocess
        serialized_request = None
        if request_data:
            if hasattr(request_data, 'method'):  # aiohttp Request object
                # Extract relevant request data
                serialized_request = {
                    'method': request_data.method,
                    'url': str(request_data.url),
                    'path': request_data.path,
                    'query_string': request_data.query_string,
                    'headers': dict(request_data.headers),
                    'content_type': request_data.content_type,
                    'body': await request_data.read() if hasattr(request_data, 'read') else None
                }
                # Convert body to base64 if it's bytes
                if isinstance(serialized_request['body'], bytes):
                    serialized_request['body'] = base64.b64encode(serialized_request['body']).decode('utf-8')
                    serialized_request['body_is_base64'] = True
            else:
                serialized_request = request_data
        
        # Create temporary files for communication
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as input_file:
            if serialized_request:
                json.dump(serialized_request, input_file)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # Create subprocess execution script
            exec_script = f'''
import sys
import json
import asyncio
import base64
from pathlib import Path
sys.path.insert(0, "{os.path.dirname(script_path)}")

{self._get_mock_classes_code()}

async def main():
    try:
        # Load the target script
        import importlib.util
        spec = importlib.util.spec_from_file_location("target_script", "{script_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Load input data
        request_data = None
        try:
            with open("{input_path}", "r") as f:
                content = f.read().strip()
                if content:
                    request_data = json.loads(content)
        except:
            pass
        
        # Create mock objects
        mock_request = MockRequest(request_data)
        mock_service = MockService("proserve-subprocess")
        
        # Execute the script with proper signature detection
        result = None
        if hasattr(module, 'main'):
            import inspect
            sig = inspect.signature(module.main)
            param_count = len(sig.parameters)
            
            if param_count == 1:
                # Background task signature: main(service)
                result = await module.main(mock_service)
            elif param_count == 2:
                # Endpoint signature: main(request, service)
                result = await module.main(mock_request, mock_service)
            else:
                # Try with both parameters, fallback to service only
                try:
                    result = await module.main(mock_request, mock_service)
                except TypeError:
                    result = await module.main(mock_service)
                    
        elif hasattr(module, 'handler'):
            import inspect
            sig = inspect.signature(module.handler)
            param_count = len(sig.parameters)
            
            if param_count == 1:
                # Background task signature: handler(service)  
                result = await module.handler(mock_service)
            elif param_count == 2:
                # Endpoint signature: handler(request, service)
                result = await module.handler(mock_request, mock_service)
            else:
                # Try with both parameters, fallback to service only
                try:
                    result = await module.handler(mock_request, mock_service)
                except TypeError:
                    result = await module.handler(mock_service)
        else:
            raise AttributeError("Script must have main or handler function")
        
        # Handle different result types
        if hasattr(result, 'status'):  # aiohttp Response object
            result_data = {{
                'status': result.status,
                'headers': dict(result.headers) if hasattr(result, 'headers') else {{}},
                'body': result.text if hasattr(result, 'text') else str(result)
            }}
        elif isinstance(result, dict):
            result_data = result
        else:
            result_data = {{'data': str(result)}}
        
        # Save result
        with open("{output_path}", "w") as f:
            json.dump({{"status": "success", "data": result_data}}, f)
    
    except Exception as e:
        import traceback
        with open("{output_path}", "w") as f:
            json.dump({{"status": "error", "error": str(e), "traceback": traceback.format_exc()}}, f)

if __name__ == "__main__":
    asyncio.run(main())
'''
            
            # Write execution script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as exec_file:
                exec_file.write(exec_script)
                exec_path = exec_file.name
            
            # Execute subprocess
            cmd = [sys.executable, exec_path]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.timeout
                )
                
                # Load result
                with open(output_path, 'r') as f:
                    result = json.load(f)
                
                if result['status'] == 'error':
                    error_msg = result['error']
                    if 'traceback' in result:
                        service.logger.error(f"Subprocess traceback: {result['traceback']}")
                    raise RuntimeError(f"Script execution failed: {error_msg}")
                
                # Convert result back to aiohttp Response if needed
                result_data = result['data']
                if isinstance(result_data, dict) and 'status' in result_data:
                    # This looks like a response object
                    try:
                        from aiohttp import web
                        response_body = result_data.get('body', result_data.get('data', ''))
                        return web.Response(
                            text=str(response_body),
                            status=result_data.get('status', 200),
                            headers=result_data.get('headers', {})
                        )
                    except ImportError:
                        # If aiohttp not available, return raw data
                        return result_data
                else:
                    # Return raw data (for background tasks or simple responses)
                    return result_data
                
            except asyncio.TimeoutError:
                process.kill()
                raise RuntimeError(f"Script execution timed out after {self.timeout} seconds")
        
        finally:
            # Cleanup temporary files
            for path in [input_path, output_path, exec_path]:
                try:
                    os.unlink(path)
                except OSError:
                    pass
    
    async def _execute_container(self, script_path: str, service, request_data: Any, script_context = None) -> Any:
        """Execute script in Docker container for full isolation"""
        service.logger.warning("Container isolation not yet implemented, falling back to subprocess")
        return await self._execute_subprocess(script_path, service, request_data, script_context)
    
    async def _execute_docker(self, script_path: str, service, request_data: Any, script_context = None) -> Any:
        """Execute script in Docker container with automatic environment selection"""
        if not self.docker_manager:
            service.logger.error("❌ Docker isolation manager not available, falling back to subprocess")
            return await self._execute_subprocess(script_path, service, request_data, script_context)
        
        try:
            service.logger.info(f"🐳 Executing script in Docker environment: {script_path}")
            
            # Execute script using Docker isolation manager with automatic environment selection
            result = await self.docker_manager.execute_script_isolated(
                script_path=script_path,
                service=service,
                request_data=request_data,
                script_context=script_context,
                force_environment=self.force_environment
            )
            
            # Check execution result
            if result.exit_code == 0:
                service.logger.info(f"✅ Docker execution successful: {result.container_id}")
                service.logger.debug(f"Environment: {result.environment_type}, Time: {result.execution_time:.2f}s")
                return result.stdout
            else:
                service.logger.error(f"❌ Docker execution failed: {result.container_id}")
                service.logger.error(f"Exit code: {result.exit_code}")
                service.logger.error(f"Error output: {result.stderr}")
                raise RuntimeError(f"Docker script execution failed: {result.stderr}")
                
        except Exception as e:
            service.logger.error(f"❌ Docker isolation execution failed: {e}")
            
            # Fallback to subprocess if Docker fails
            if self.config.get('fallback_on_docker_failure', True):
                service.logger.warning("⚠️  Falling back to subprocess isolation")
                return await self._execute_subprocess(script_path, service, request_data, script_context)
            else:
                raise
    
    async def _execute_sandbox(self, script_path: str, service, request_data: Any, script_context = None) -> Any:
        """Execute script in sandboxed environment"""
        service.logger.warning("Sandbox isolation not yet implemented, falling back to subprocess")
        return await self._execute_subprocess(script_path, service, request_data, script_context)
    
    async def _load_and_execute_script(self, script_path: str, service, request_data: Any, script_context = None) -> Any:
        """Load and execute script directly with enhanced logging context"""
        
        # Create script-specific logger with enhanced context if available
        if PROSERVE_LOGGING_AVAILABLE and script_context:
            script_logger = setup_logging(
                context=script_context,
                debug=os.getenv("DEBUG", "false").lower() == "true",
                console_output=True,
                json_output=False  # Use readable format for direct execution
            )
            script_logger.info(f"Loading script module", script_path=script_path)
        else:
            script_logger = service.logger
            
        try:
            spec = importlib.util.spec_from_file_location("script", script_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not create module spec for {script_path}")
            
            module = importlib.util.module_from_spec(spec)
            script_logger.debug(f"Executing script module", script_path=script_path)
            spec.loader.exec_module(module)
            
            # Execute the appropriate function with enhanced logging
            if hasattr(module, 'main'):
                script_logger.debug(f"Calling main() function", script_path=script_path)
                result = await module.main(request_data, service)
                script_logger.info(f"Script main() completed successfully", script_path=script_path)
                return result
            elif hasattr(module, 'handler'):
                script_logger.debug(f"Calling handler() function", script_path=script_path)
                result = await module.handler(request_data, service)
                script_logger.info(f"Script handler() completed successfully", script_path=script_path)
                return result
            else:
                error_msg = f"Script {script_path} must have a 'main' or 'handler' function"
                script_logger.error(error_msg, script_path=script_path)
                raise AttributeError(error_msg)
                
        except Exception as e:
            if PROSERVE_LOGGING_AVAILABLE and script_context:
                script_logger.error(f"Script execution failed: {e}", 
                                  script_path=script_path,
                                  error_type=type(e).__name__,
                                  isolation_mode=script_context.isolation_mode if hasattr(script_context, 'isolation_mode') else self.mode)
            else:
                service.logger.error(f"Script execution failed: {e}", script=script_path)
            raise

    def _get_mock_classes_code(self) -> str:
        """Generate Mock classes code for subprocess execution"""
        return '''
class MockRequest:
    """Mock request object for subprocess execution"""
    def __init__(self, data):
        if data:
            self.method = data.get('method', 'GET')
            self.path = data.get('path', '/')
            self.query_string = data.get('query_string', '')
            self.headers = data.get('headers', {})
            self.content_type = data.get('content_type', 'application/json')
            self._body = data.get('body')
            self._body_is_base64 = data.get('body_is_base64', False)
        else:
            self.method = 'GET'
            self.path = '/'
            self.query_string = ''
            self.headers = {}
            self.content_type = 'application/json'
            self._body = None
            self._body_is_base64 = False
    
    async def json(self):
        if self._body:
            if self._body_is_base64:
                body = base64.b64decode(self._body).decode('utf-8')
            else:
                body = self._body
            return json.loads(body) if isinstance(body, str) else body
        return {}
    
    async def text(self):
        if self._body:
            if self._body_is_base64:
                return base64.b64decode(self._body).decode('utf-8')
            return self._body
        return ""
    
    async def read(self):
        if self._body:
            if self._body_is_base64:
                return base64.b64decode(self._body)
            return self._body.encode('utf-8') if isinstance(self._body, str) else self._body
        return b""

class MockLogger:
    """Mock logger for subprocess execution"""
    def info(self, msg, **kwargs):
        print(f"[INFO] {msg} {kwargs}")
    
    def error(self, msg, **kwargs):
        print(f"[ERROR] {msg} {kwargs}")
    
    def warning(self, msg, **kwargs):
        print(f"[WARNING] {msg} {kwargs}")
    
    def debug(self, msg, **kwargs):
        print(f"[DEBUG] {msg} {kwargs}")

class MockService:
    """Mock service object for subprocess execution"""
    def __init__(self, service_name="proserve-subprocess"):
        self.logger = MockLogger()
        self.name = service_name
        self.proserve_client = None
        self.websocket_connections = set()
    
    def __getattr__(self, name):
        return None
'''

    def get_available_environments(self) -> Dict[str, bool]:
        """Get information about available isolation environments"""
        return {
            'direct': True,
            'subprocess': True,
            'docker': DOCKER_ISOLATION_AVAILABLE and self.docker_manager is not None,
            'micropython': EXTENDED_ENVIRONMENTS_AVAILABLE and self.micropython_manager is not None,
            'arduino': EXTENDED_ENVIRONMENTS_AVAILABLE and self.arduino_manager is not None,
            'sandbox': False  # Not yet implemented
        }

    def get_platform_info(self) -> Dict[str, Any]:
        """Get platform-specific information"""
        return {
            'mode': self.mode,
            'platform': self.platform,
            'board': self.board,
            'timeout': self.timeout,
            'available_environments': self.get_available_environments(),
            'extended_environments_available': EXTENDED_ENVIRONMENTS_AVAILABLE,
            'docker_available': DOCKER_ISOLATION_AVAILABLE
        }
