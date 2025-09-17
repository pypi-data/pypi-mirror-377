"""
ProServe Mock Manager - Mock System Management and Coordination
Manages mock services, configurations, and request logging for testing and development
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from .mock_types import MockService, MockEndpoint, MockResponse, MockRequest, generate_sample_user_data, generate_sample_product_data, generate_sample_order_data
from .mock_handler import MockRequestHandler, create_mock_handler_for_service


logger = structlog.get_logger(__name__)


class MockSystemManager:
    """Manages service alternatives and mock responses"""
    
    def __init__(self, mock_data_dir: Path = None):
        self.mock_data_dir = mock_data_dir or Path('mock_data')
        self.mock_data_dir.mkdir(exist_ok=True)
        
        self.mock_services: Dict[str, MockService] = {}
        self.active_mocks: Dict[str, bool] = {}  # endpoint_key -> enabled
        self.request_logs: List[MockRequest] = []
        self.max_log_size = 1000
        
        self.logger = logging.getLogger(__name__)
        
        # Request handlers for each service
        self.handlers: Dict[str, MockRequestHandler] = {}
        
        # Load existing mock configurations
        self._load_mock_configurations()
        
        # Create default demo data if none exists
        if not self.mock_services:
            self._ensure_demo_data()
    
    def _load_mock_configurations(self):
        """Load mock configurations from JSON files"""
        self.logger.info(f"Loading mock configurations from {self.mock_data_dir}")
        
        for config_file in self.mock_data_dir.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                
                mock_service = MockService.from_dict(data)
                self.mock_services[mock_service.name] = mock_service
                
                # Initialize all endpoints as active by default
                for endpoint in mock_service.endpoints:
                    endpoint_key = endpoint.get_endpoint_key()
                    self.active_mocks[endpoint_key] = True
                
                self.logger.info(f"Loaded mock service: {mock_service.name} with {len(mock_service.endpoints)} endpoints")
                
            except Exception as e:
                self.logger.error(f"Failed to load mock configuration from {config_file}: {e}")
    
    def _ensure_demo_data(self):
        """Create demo mock data if none exists"""
        self.logger.info("Creating default demo mock data")
        
        # Create demo services
        self._create_user_service_mock()
        self._create_system_service_mock() 
        self._create_health_service_mock()
        self._create_grpc_service_mock()
        
        # Save demo data to files
        for service_name, service in self.mock_services.items():
            config_file = self.mock_data_dir / f"{service_name}.json"
            service.export_to_file(config_file)
    
    def _create_user_service_mock(self):
        """Create demo user service mock"""
        user_service = MockService(
            name="user-service",
            version="1.0.0",
            description="Demo user management service",
            global_headers={"X-Service": "user-service"}
        )
        
        # GET /users - list users
        list_users_endpoint = MockEndpoint(
            path="/users",
            method="GET",
            description="List all users",
            tags=["users", "list"]
        )
        list_users_endpoint.add_response(MockResponse(
            status=200,
            body={
                "users": [generate_sample_user_data() for _ in range(5)],
                "total": 5,
                "page": 1,
                "per_page": 10
            }
        ))
        user_service.add_endpoint(list_users_endpoint)
        
        # GET /users/{id} - get user by ID
        get_user_endpoint = MockEndpoint(
            path="/users/{id}",
            method="GET", 
            description="Get user by ID",
            tags=["users", "get"]
        )
        get_user_endpoint.add_response(MockResponse(
            status=200,
            body=generate_sample_user_data()
        ))
        get_user_endpoint.add_response(MockResponse(
            status=404,
            body={"error": "User not found", "id": "{id}"},
            probability=0.1
        ))
        user_service.add_endpoint(get_user_endpoint)
        
        # POST /users - create user
        create_user_endpoint = MockEndpoint(
            path="/users",
            method="POST",
            description="Create new user",
            tags=["users", "create"]
        )
        create_user_endpoint.add_response(MockResponse(
            status=201,
            body={
                **generate_sample_user_data(),
                "message": "User created successfully"
            }
        ))
        user_service.add_endpoint(create_user_endpoint)
        
        # PUT /users/{id} - update user
        update_user_endpoint = MockEndpoint(
            path="/users/{id}",
            method="PUT",
            description="Update user",
            tags=["users", "update"]
        )
        update_user_endpoint.add_response(MockResponse(
            status=200,
            body={
                **generate_sample_user_data(),
                "message": "User updated successfully",
                "updated_at": "{{timestamp}}"
            }
        ))
        user_service.add_endpoint(update_user_endpoint)
        
        # DELETE /users/{id} - delete user
        delete_user_endpoint = MockEndpoint(
            path="/users/{id}",
            method="DELETE",
            description="Delete user", 
            tags=["users", "delete"]
        )
        delete_user_endpoint.add_response(MockResponse(
            status=200,
            body={"message": "User deleted successfully", "id": "{id}"}
        ))
        user_service.add_endpoint(delete_user_endpoint)
        
        self.mock_services["user-service"] = user_service
    
    def _create_system_service_mock(self):
        """Create demo system service mock"""
        system_service = MockService(
            name="system-service",
            version="1.0.0", 
            description="Demo system management service",
            global_delay=0.1
        )
        
        # GET /system/info - system information
        info_endpoint = MockEndpoint(
            path="/system/info",
            method="GET",
            description="Get system information"
        )
        info_endpoint.add_response(MockResponse(
            status=200,
            body={
                "system": "ProServe Mock System",
                "version": "1.0.0",
                "uptime": "{{random_id}} seconds",
                "timestamp": "{{timestamp}}",
                "environment": "development"
            }
        ))
        system_service.add_endpoint(info_endpoint)
        
        # GET /system/status - system status
        status_endpoint = MockEndpoint(
            path="/system/status",
            method="GET",
            description="Get system status"
        )
        status_endpoint.add_response(MockResponse(
            status=200,
            body={
                "status": "healthy",
                "services": {
                    "database": "connected",
                    "cache": "connected", 
                    "messaging": "connected"
                },
                "timestamp": "{{timestamp}}"
            }
        ))
        system_service.add_endpoint(status_endpoint)
        
        self.mock_services["system-service"] = system_service
    
    def _create_health_service_mock(self):
        """Create demo health service mock"""
        health_service = MockService(
            name="health-service",
            version="1.0.0",
            description="Demo health check service"
        )
        
        # GET /health - basic health check
        health_endpoint = MockEndpoint(
            path="/health", 
            method="GET",
            description="Basic health check"
        )
        health_endpoint.add_response(MockResponse(
            status=200,
            body={
                "status": "healthy",
                "timestamp": "{{timestamp}}",
                "version": "1.0.0"
            }
        ))
        health_service.add_endpoint(health_endpoint)
        
        # GET /health/detailed - detailed health check
        detailed_health_endpoint = MockEndpoint(
            path="/health/detailed",
            method="GET", 
            description="Detailed health check"
        )
        detailed_health_endpoint.add_response(MockResponse(
            status=200,
            body={
                "status": "healthy",
                "checks": {
                    "database": {"status": "healthy", "latency": "2ms"},
                    "cache": {"status": "healthy", "latency": "1ms"},
                    "external_api": {"status": "healthy", "latency": "45ms"}
                },
                "uptime": "{{random_id}} seconds", 
                "timestamp": "{{timestamp}}"
            }
        ))
        health_service.add_endpoint(detailed_health_endpoint)
        
        self.mock_services["health-service"] = health_service
    
    def _create_grpc_service_mock(self):
        """Create demo gRPC service mock (HTTP representation)"""
        grpc_service = MockService(
            name="grpc-service",
            version="1.0.0",
            description="Demo gRPC service (HTTP gateway)"
        )
        
        # POST /v1/products - gRPC-style product service
        products_endpoint = MockEndpoint(
            path="/v1/products",
            method="POST",
            description="gRPC-style product operations"
        )
        products_endpoint.add_response(MockResponse(
            status=200,
            body=generate_sample_product_data()
        ))
        grpc_service.add_endpoint(products_endpoint)
        
        # POST /v1/orders - gRPC-style order service
        orders_endpoint = MockEndpoint(
            path="/v1/orders",
            method="POST", 
            description="gRPC-style order operations"
        )
        orders_endpoint.add_response(MockResponse(
            status=200,
            body=generate_sample_order_data()
        ))
        grpc_service.add_endpoint(orders_endpoint)
        
        self.mock_services["grpc-service"] = grpc_service
    
    def create_mock_handler(self, service_name: str) -> Optional[callable]:
        """Create aiohttp handler for a mock service"""
        if service_name not in self.mock_services:
            self.logger.warning(f"Mock service not found: {service_name}")
            return None
        
        mock_service = self.mock_services[service_name]
        handler = create_mock_handler_for_service(mock_service)
        
        # Store handler for stats
        self.handlers[service_name] = handler._handler_instance
        
        return handler
    
    def get_mock_service(self, service_name: str) -> Optional[MockService]:
        """Get mock service by name"""
        return self.mock_services.get(service_name)
    
    def add_mock_service(self, mock_service: MockService):
        """Add or update a mock service"""
        self.mock_services[mock_service.name] = mock_service
        
        # Initialize endpoints as active
        for endpoint in mock_service.endpoints:
            endpoint_key = endpoint.get_endpoint_key()
            self.active_mocks[endpoint_key] = True
        
        # Save to file
        config_file = self.mock_data_dir / f"{mock_service.name}.json"
        mock_service.export_to_file(config_file)
        
        self.logger.info(f"Added mock service: {mock_service.name}")
    
    def remove_mock_service(self, service_name: str) -> bool:
        """Remove a mock service"""
        if service_name not in self.mock_services:
            return False
        
        # Remove service
        mock_service = self.mock_services[service_name]
        del self.mock_services[service_name]
        
        # Remove endpoint activations
        for endpoint in mock_service.endpoints:
            endpoint_key = endpoint.get_endpoint_key()
            self.active_mocks.pop(endpoint_key, None)
        
        # Remove handler
        self.handlers.pop(service_name, None)
        
        # Remove config file
        config_file = self.mock_data_dir / f"{service_name}.json"
        if config_file.exists():
            config_file.unlink()
        
        self.logger.info(f"Removed mock service: {service_name}")
        return True
    
    def list_mock_services(self) -> List[str]:
        """List available mock service names"""
        return list(self.mock_services.keys())
    
    def enable_mock_endpoint(self, service_name: str, path: str, method: str):
        """Enable a specific mock endpoint"""
        endpoint_key = f"{method.upper()}:{path}"
        self.active_mocks[endpoint_key] = True
        self.logger.info(f"Enabled mock endpoint: {endpoint_key}")
    
    def disable_mock_endpoint(self, service_name: str, path: str, method: str):
        """Disable a specific mock endpoint"""
        endpoint_key = f"{method.upper()}:{path}"
        self.active_mocks[endpoint_key] = False
        self.logger.info(f"Disabled mock endpoint: {endpoint_key}")
    
    def is_mock_endpoint_enabled(self, service_name: str, path: str, method: str) -> bool:
        """Check if a mock endpoint is enabled"""
        endpoint_key = f"{method.upper()}:{path}"
        return self.active_mocks.get(endpoint_key, True)
    
    def log_request(self, mock_request: MockRequest):
        """Log a mock request"""
        self.request_logs.append(mock_request)
        
        # Trim logs if they exceed max size
        if len(self.request_logs) > self.max_log_size:
            self.request_logs = self.request_logs[-self.max_log_size:]
    
    def get_request_logs(self, limit: int = 100) -> List[MockRequest]:
        """Get recent request logs"""
        return self.request_logs[-limit:]
    
    def clear_request_logs(self):
        """Clear request logs"""
        self.request_logs.clear()
        self.logger.info("Cleared mock request logs")
    
    def export_mock_configuration(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Export mock service configuration"""
        if service_name not in self.mock_services:
            return None
        
        return self.mock_services[service_name].to_dict()
    
    def import_mock_configuration(self, config: Dict[str, Any]) -> bool:
        """Import mock service configuration"""
        try:
            mock_service = MockService.from_dict(config)
            self.add_mock_service(mock_service)
            return True
        except Exception as e:
            self.logger.error(f"Failed to import mock configuration: {e}")
            return False
    
    def get_mock_stats(self) -> Dict[str, Any]:
        """Get mock system statistics"""
        total_endpoints = sum(len(service.endpoints) for service in self.mock_services.values())
        active_endpoints = sum(1 for enabled in self.active_mocks.values() if enabled)
        
        handler_stats = {}
        for service_name, handler in self.handlers.items():
            handler_stats[service_name] = handler.get_stats()
        
        return {
            "total_services": len(self.mock_services),
            "total_endpoints": total_endpoints,
            "active_endpoints": active_endpoints,
            "total_requests_logged": len(self.request_logs),
            "max_log_size": self.max_log_size,
            "mock_data_directory": str(self.mock_data_dir),
            "handler_stats": handler_stats
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.clear_request_logs()
        for handler in self.handlers.values():
            handler.reset_stats()
        self.logger.info("Reset mock system statistics")
    
    def backup_configurations(self, backup_path: Path = None) -> Path:
        """Backup all mock configurations"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.mock_data_dir / f"backup_{timestamp}"
        
        backup_path.mkdir(exist_ok=True)
        
        for service_name, service in self.mock_services.items():
            backup_file = backup_path / f"{service_name}.json"
            service.export_to_file(backup_file)
        
        self.logger.info(f"Backed up mock configurations to {backup_path}")
        return backup_path
    
    def restore_configurations(self, backup_path: Path) -> bool:
        """Restore mock configurations from backup"""
        try:
            if not backup_path.exists():
                self.logger.error(f"Backup path does not exist: {backup_path}")
                return False
            
            # Clear current configurations
            self.mock_services.clear()
            self.active_mocks.clear()
            self.handlers.clear()
            
            # Load from backup
            for config_file in backup_path.glob("*.json"):
                try:
                    mock_service = MockService.import_from_file(config_file)
                    self.add_mock_service(mock_service)
                except Exception as e:
                    self.logger.error(f"Failed to restore service from {config_file}: {e}")
            
            self.logger.info(f"Restored mock configurations from {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore configurations: {e}")
            return False


# Global mock system instance
_mock_system: Optional[MockSystemManager] = None


def get_mock_system(mock_data_dir: Path = None) -> MockSystemManager:
    """Get or create global mock system instance"""
    global _mock_system
    if _mock_system is None:
        _mock_system = MockSystemManager(mock_data_dir)
    return _mock_system


def reset_mock_system():
    """Reset the global mock system instance"""
    global _mock_system
    _mock_system = None
