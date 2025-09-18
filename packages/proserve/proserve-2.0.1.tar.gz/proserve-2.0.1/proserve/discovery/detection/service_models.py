"""
ProServe Service Detection Models - Service Detection Data Structures
Defines data models and types used for service detection and analysis
"""

import json
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class MigrationDifficulty(Enum):
    """Migration difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class Framework(Enum):
    """Supported web frameworks"""
    FLASK = "flask"
    FASTAPI = "fastapi"
    DJANGO = "django"
    STARLETTE = "starlette"
    TORNADO = "tornado"
    AIOHTTP = "aiohttp"
    BOTTLE = "bottle"
    CHERRYPY = "cherrypy"
    PYRAMID = "pyramid"
    SANIC = "sanic"
    QUART = "quart"
    EXPRESS = "express"
    NODEJS = "nodejs"
    SPRING_BOOT = "spring_boot"
    UNKNOWN = "unknown"


@dataclass
class EndpointInfo:
    """Information about a detected endpoint"""
    path: str
    method: str
    handler_name: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    decorators: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'path': self.path,
            'method': self.method,
            'handler_name': self.handler_name,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'decorators': self.decorators,
            'parameters': self.parameters,
            'return_type': self.return_type
        }


@dataclass
class DatabaseInfo:
    """Information about detected database usage"""
    type: str  # postgresql, mysql, sqlite, mongodb, etc.
    connection_info: Dict[str, Any] = field(default_factory=dict)
    models: List[str] = field(default_factory=list)
    migrations: List[str] = field(default_factory=list)
    orm: Optional[str] = None  # sqlalchemy, django-orm, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'type': self.type,
            'connection_info': self.connection_info,
            'models': self.models,
            'migrations': self.migrations,
            'orm': self.orm
        }


@dataclass
class DeploymentInfo:
    """Information about deployment configuration"""
    platform: Optional[str] = None  # docker, kubernetes, heroku, etc.
    config_files: List[str] = field(default_factory=list)
    environment_vars: List[str] = field(default_factory=list)
    build_commands: List[str] = field(default_factory=list)
    run_commands: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'platform': self.platform,
            'config_files': self.config_files,
            'environment_vars': self.environment_vars,
            'build_commands': self.build_commands,
            'run_commands': self.run_commands
        }


@dataclass
class ServiceInfo:
    """Comprehensive service information from detection"""
    name: str
    framework: Framework
    version: Optional[str] = None
    path: Optional[Path] = None
    entry_point: Optional[str] = None
    config_files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    endpoints: List[EndpointInfo] = field(default_factory=list)
    database_info: Optional[DatabaseInfo] = None
    deployment_info: Optional[DeploymentInfo] = None
    complexity_score: int = 0
    migration_difficulty: MigrationDifficulty = MigrationDifficulty.MEDIUM
    confidence_score: float = 0.0  # 0.0 - 1.0
    
    def __post_init__(self):
        """Validate and process service info after initialization"""
        if isinstance(self.framework, str):
            try:
                self.framework = Framework(self.framework)
            except ValueError:
                self.framework = Framework.UNKNOWN
        
        if isinstance(self.migration_difficulty, str):
            try:
                self.migration_difficulty = MigrationDifficulty(self.migration_difficulty)
            except ValueError:
                self.migration_difficulty = MigrationDifficulty.MEDIUM
        
        # Ensure confidence score is in valid range
        self.confidence_score = max(0.0, min(1.0, self.confidence_score))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'framework': self.framework.value,
            'version': self.version,
            'path': str(self.path) if self.path else None,
            'entry_point': self.entry_point,
            'config_files': self.config_files,
            'dependencies': self.dependencies,
            'endpoints': [ep.to_dict() for ep in self.endpoints],
            'database_info': self.database_info.to_dict() if self.database_info else None,
            'deployment_info': self.deployment_info.to_dict() if self.deployment_info else None,
            'complexity_score': self.complexity_score,
            'migration_difficulty': self.migration_difficulty.value,
            'confidence_score': self.confidence_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ServiceInfo':
        """Create from dictionary"""
        # Parse endpoints
        endpoints = []
        for ep_data in data.get('endpoints', []):
            endpoints.append(EndpointInfo(**ep_data))
        
        # Parse database info
        database_info = None
        if data.get('database_info'):
            database_info = DatabaseInfo(**data['database_info'])
        
        # Parse deployment info
        deployment_info = None
        if data.get('deployment_info'):
            deployment_info = DeploymentInfo(**data['deployment_info'])
        
        return cls(
            name=data['name'],
            framework=data.get('framework', 'unknown'),
            version=data.get('version'),
            path=Path(data['path']) if data.get('path') else None,
            entry_point=data.get('entry_point'),
            config_files=data.get('config_files', []),
            dependencies=data.get('dependencies', []),
            endpoints=endpoints,
            database_info=database_info,
            deployment_info=deployment_info,
            complexity_score=data.get('complexity_score', 0),
            migration_difficulty=data.get('migration_difficulty', 'medium'),
            confidence_score=data.get('confidence_score', 0.0)
        )
    
    def add_endpoint(self, endpoint: EndpointInfo):
        """Add an endpoint to the service"""
        self.endpoints.append(endpoint)
    
    def get_endpoints_by_method(self, method: str) -> List[EndpointInfo]:
        """Get endpoints by HTTP method"""
        return [ep for ep in self.endpoints if ep.method.upper() == method.upper()]
    
    def get_endpoints_by_path_pattern(self, pattern: str) -> List[EndpointInfo]:
        """Get endpoints matching path pattern"""
        import re
        compiled_pattern = re.compile(pattern)
        return [ep for ep in self.endpoints if compiled_pattern.search(ep.path)]
    
    def calculate_api_complexity(self) -> int:
        """Calculate API complexity based on endpoints"""
        if not self.endpoints:
            return 0
        
        # Base score from number of endpoints
        score = len(self.endpoints)
        
        # Add complexity for different HTTP methods
        methods = set(ep.method for ep in self.endpoints)
        score += len(methods) * 2
        
        # Add complexity for parameterized paths
        param_paths = sum(1 for ep in self.endpoints if '{' in ep.path or '<' in ep.path)
        score += param_paths * 3
        
        # Add complexity for endpoints with many parameters
        complex_endpoints = sum(1 for ep in self.endpoints if len(ep.parameters) > 3)
        score += complex_endpoints * 2
        
        return score
    
    def estimate_migration_effort(self) -> Dict[str, Any]:
        """Estimate migration effort to ProServe"""
        effort = {
            'difficulty': self.migration_difficulty.value,
            'estimated_hours': 0,
            'blockers': [],
            'recommendations': []
        }
        
        # Base effort from complexity
        base_hours = min(self.complexity_score * 0.5, 40)
        
        # Framework-specific adjustments
        if self.framework == Framework.FLASK:
            base_hours *= 0.8  # Flask is simpler to migrate
            effort['recommendations'].append("Flask applications typically migrate easily to ProServe")
        elif self.framework == Framework.FASTAPI:
            base_hours *= 0.7  # FastAPI is very similar
            effort['recommendations'].append("FastAPI applications map well to ProServe's async model")
        elif self.framework == Framework.DJANGO:
            base_hours *= 1.5  # Django is more complex
            effort['blockers'].append("Django ORM and admin interface need special consideration")
        
        # Database complexity
        if self.database_info:
            if len(self.database_info.models) > 10:
                base_hours += 8
                effort['blockers'].append("Complex database schema with many models")
            if self.database_info.orm == 'django-orm':
                base_hours += 4
                effort['blockers'].append("Django ORM migration required")
        
        # Endpoint complexity
        if len(self.endpoints) > 20:
            base_hours += 6
            effort['blockers'].append("Large number of endpoints to migrate")
        
        effort['estimated_hours'] = int(base_hours)
        
        return effort
    
    def export_proserve_manifest(self) -> Dict[str, Any]:
        """Generate a basic ProServe manifest from detected service info"""
        manifest = {
            'name': self.name,
            'version': self.version or '1.0.0',
            'description': f'Migrated {self.framework.value} service',
            'endpoints': []
        }
        
        # Convert endpoints
        for endpoint in self.endpoints:
            manifest_endpoint = {
                'path': endpoint.path,
                'method': endpoint.method.lower(),
                'handler': endpoint.handler_name or 'handler'
            }
            
            if endpoint.parameters:
                manifest_endpoint['parameters'] = endpoint.parameters
            
            manifest['endpoints'].append(manifest_endpoint)
        
        # Add database configuration if detected
        if self.database_info:
            manifest['databases'] = [{
                'name': 'main',
                'type': self.database_info.type,
                'connection': self.database_info.connection_info
            }]
        
        return manifest


@dataclass
class DetectionResult:
    """Result of service detection process"""
    services: List[ServiceInfo] = field(default_factory=list)
    total_files_scanned: int = 0
    detection_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'services': [service.to_dict() for service in self.services],
            'total_files_scanned': self.total_files_scanned,
            'detection_time': self.detection_time,
            'errors': self.errors,
            'warnings': self.warnings,
            'summary': {
                'total_services': len(self.services),
                'frameworks_detected': list(set(s.framework.value for s in self.services)),
                'average_confidence': sum(s.confidence_score for s in self.services) / len(self.services) if self.services else 0.0
            }
        }
    
    def add_service(self, service: ServiceInfo):
        """Add a detected service"""
        self.services.append(service)
    
    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add a warning message"""
        self.warnings.append(warning)
    
    def get_services_by_framework(self, framework: Framework) -> List[ServiceInfo]:
        """Get services by framework type"""
        return [s for s in self.services if s.framework == framework]
    
    def get_high_confidence_services(self, threshold: float = 0.7) -> List[ServiceInfo]:
        """Get services with high confidence scores"""
        return [s for s in self.services if s.confidence_score >= threshold]


# Utility functions for working with detection models
def create_endpoint_from_route_info(path: str, method: str, **kwargs) -> EndpointInfo:
    """Create EndpointInfo from route information"""
    return EndpointInfo(
        path=path,
        method=method.upper(),
        handler_name=kwargs.get('handler_name'),
        file_path=kwargs.get('file_path'),
        line_number=kwargs.get('line_number'),
        decorators=kwargs.get('decorators', []),
        parameters=kwargs.get('parameters', []),
        return_type=kwargs.get('return_type')
    )


def create_basic_service_info(name: str, framework: str, path: Path = None) -> ServiceInfo:
    """Create basic ServiceInfo with minimal required data"""
    return ServiceInfo(
        name=name,
        framework=Framework(framework) if framework in [f.value for f in Framework] else Framework.UNKNOWN,
        path=path,
        confidence_score=0.5  # Default medium confidence
    )


def merge_service_info(primary: ServiceInfo, secondary: ServiceInfo) -> ServiceInfo:
    """Merge two ServiceInfo objects, preferring primary for conflicts"""
    merged = ServiceInfo(
        name=primary.name,
        framework=primary.framework,
        version=primary.version or secondary.version,
        path=primary.path or secondary.path,
        entry_point=primary.entry_point or secondary.entry_point,
        config_files=list(set(primary.config_files + secondary.config_files)),
        dependencies=list(set(primary.dependencies + secondary.dependencies)),
        endpoints=primary.endpoints + secondary.endpoints,
        database_info=primary.database_info or secondary.database_info,
        deployment_info=primary.deployment_info or secondary.deployment_info,
        complexity_score=max(primary.complexity_score, secondary.complexity_score),
        migration_difficulty=primary.migration_difficulty,  # Keep primary
        confidence_score=max(primary.confidence_score, secondary.confidence_score)
    )
    
    return merged
