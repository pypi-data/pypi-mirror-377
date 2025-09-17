"""
ProServe Framework Detector - Framework Detection and Analysis
Detects web frameworks and analyzes their usage patterns in source code
"""

import re
import ast
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
import structlog

from .service_models import Framework, ServiceInfo, EndpointInfo, DatabaseInfo, DeploymentInfo


logger = structlog.get_logger(__name__)


class FrameworkDetector:
    """Advanced framework detection with confidence scoring"""
    
    def __init__(self):
        # Framework detection patterns and configurations
        self.framework_patterns = {
            Framework.FLASK: {
                'import_patterns': [
                    r'from\s+flask\s+import',
                    r'import\s+flask',
                    r'Flask\(__name__\)'
                ],
                'decorator_patterns': [
                    r'@app\.route\(',
                    r'@bp\.route\(',
                    r'@blueprint\.route\('
                ],
                'config_files': ['config.py', 'settings.py', 'instance/config.py'],
                'common_files': ['app.py', 'main.py', 'run.py', 'wsgi.py'],
                'dependencies': ['flask', 'werkzeug', 'jinja2']
            },
            Framework.FASTAPI: {
                'import_patterns': [
                    r'from\s+fastapi\s+import',
                    r'import\s+fastapi',
                    r'FastAPI\('
                ],
                'decorator_patterns': [
                    r'@app\.get\(',
                    r'@app\.post\(',
                    r'@app\.put\(',
                    r'@app\.delete\(',
                    r'@router\.get\(',
                    r'@router\.post\('
                ],
                'config_files': ['config.py', 'settings.py', '.env'],
                'common_files': ['main.py', 'app.py', 'api.py'],
                'dependencies': ['fastapi', 'uvicorn', 'starlette', 'pydantic']
            },
            Framework.DJANGO: {
                'import_patterns': [
                    r'from\s+django\.',
                    r'import\s+django',
                    r'django\.conf\.settings'
                ],
                'decorator_patterns': [
                    r'@require_http_methods',
                    r'@csrf_exempt',
                    r'@login_required'
                ],
                'config_files': ['settings.py', 'local_settings.py', 'production.py'],
                'common_files': ['manage.py', 'wsgi.py', 'asgi.py', 'urls.py', 'views.py'],
                'dependencies': ['django', 'djangorestframework']
            },
            Framework.STARLETTE: {
                'import_patterns': [
                    r'from\s+starlette\s+import',
                    r'import\s+starlette',
                    r'Starlette\('
                ],
                'decorator_patterns': [
                    r'@app\.route\(',
                    r'Route\('
                ],
                'config_files': ['config.py', '.env'],
                'common_files': ['main.py', 'app.py'],
                'dependencies': ['starlette', 'uvicorn']
            },
            Framework.TORNADO: {
                'import_patterns': [
                    r'import\s+tornado',
                    r'from\s+tornado\s+import',
                    r'tornado\.web\.Application'
                ],
                'decorator_patterns': [],
                'config_files': ['settings.py', 'config.py'],
                'common_files': ['main.py', 'app.py', 'server.py'],
                'dependencies': ['tornado']
            },
            Framework.AIOHTTP: {
                'import_patterns': [
                    r'from\s+aiohttp\s+import',
                    r'import\s+aiohttp',
                    r'aiohttp\.web\.Application'
                ],
                'decorator_patterns': [
                    r'@routes\.get\(',
                    r'@routes\.post\('
                ],
                'common_files': ['main.py', 'app.py', 'server.py'],
                'dependencies': ['aiohttp', 'aiohttp-cors']
            }
        }
    
    def detect_framework(self, file_path: Path) -> Tuple[Framework, float]:
        """Detect web framework in file with confidence score"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            framework_scores = {}
            
            for framework, patterns in self.framework_patterns.items():
                score = self._calculate_framework_score(content, patterns)
                if score > 0:
                    framework_scores[framework] = score
            
            if not framework_scores:
                return Framework.UNKNOWN, 0.0
            
            # Get framework with highest score
            best_framework = max(framework_scores.keys(), key=lambda f: framework_scores[f])
            confidence = min(1.0, framework_scores[best_framework] / 10.0)  # Normalize to 0-1
            
            return best_framework, confidence
            
        except Exception as e:
            logger.error(f"Error detecting framework in {file_path}: {e}")
            return Framework.UNKNOWN, 0.0
    
    def _calculate_framework_score(self, content: str, patterns: Dict[str, List[str]]) -> float:
        """Calculate confidence score for a framework based on patterns"""
        score = 0.0
        
        # Check import patterns
        for pattern in patterns.get('import_patterns', []):
            matches = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
            score += matches * 3.0  # Import patterns are strong indicators
        
        # Check decorator patterns
        for pattern in patterns.get('decorator_patterns', []):
            matches = len(re.findall(pattern, content, re.IGNORECASE | re.MULTILINE))
            score += matches * 2.0  # Decorators are good indicators
        
        return score
    
    def detect_endpoints_in_file(self, file_path: Path, framework: Framework) -> List[EndpointInfo]:
        """Detect API endpoints in a source file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if framework == Framework.FLASK:
                return self._detect_flask_endpoints(content, file_path)
            elif framework == Framework.FASTAPI:
                return self._detect_fastapi_endpoints(content, file_path)
            elif framework == Framework.DJANGO:
                return self._detect_django_endpoints(content, file_path)
            elif framework == Framework.STARLETTE:
                return self._detect_starlette_endpoints(content, file_path)
            elif framework == Framework.TORNADO:
                return self._detect_tornado_endpoints(content, file_path)
            elif framework == Framework.AIOHTTP:
                return self._detect_aiohttp_endpoints(content, file_path)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error detecting endpoints in {file_path}: {e}")
            return []
    
    def _detect_flask_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect Flask endpoints using @app.route decorators"""
        endpoints = []
        
        # Pattern to match Flask route decorators
        route_pattern = r'@(?:app|bp|blueprint)\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods\s*=\s*\[([^\]]+)\])?\)'
        
        matches = re.finditer(route_pattern, content, re.MULTILINE)
        
        for match in matches:
            path = match.group(1)
            methods_str = match.group(2)
            
            # Parse methods
            methods = ['GET']  # Default method
            if methods_str:
                methods = [m.strip().strip('\'"') for m in methods_str.split(',')]
            
            # Find the function name following the decorator
            start_pos = match.end()
            remaining_content = content[start_pos:]
            func_match = re.search(r'def\s+(\w+)\s*\(([^)]*)\):', remaining_content)
            
            handler_name = None
            parameters = []
            
            if func_match:
                handler_name = func_match.group(1)
                params_str = func_match.group(2)
                if params_str:
                    parameters = [p.strip().split(':')[0].strip() for p in params_str.split(',') if p.strip()]
            
            # Create endpoint for each method
            for method in methods:
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method.upper(),
                    handler_name=handler_name,
                    file_path=str(file_path),
                    parameters=parameters,
                    decorators=['@app.route']
                ))
        
        return endpoints
    
    def _detect_fastapi_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect FastAPI endpoints using @app.get, @app.post, etc."""
        endpoints = []
        
        # Pattern to match FastAPI decorators
        method_patterns = {
            'GET': r'@(?:app|router)\.get\([\'"]([^\'"]+)[\'"]',
            'POST': r'@(?:app|router)\.post\([\'"]([^\'"]+)[\'"]',
            'PUT': r'@(?:app|router)\.put\([\'"]([^\'"]+)[\'"]',
            'DELETE': r'@(?:app|router)\.delete\([\'"]([^\'"]+)[\'"]',
            'PATCH': r'@(?:app|router)\.patch\([\'"]([^\'"]+)[\'"]'
        }
        
        for method, pattern in method_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                path = match.group(1)
                
                # Find the function name following the decorator
                start_pos = match.end()
                remaining_content = content[start_pos:]
                func_match = re.search(r'(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\):', remaining_content)
                
                handler_name = None
                parameters = []
                
                if func_match:
                    handler_name = func_match.group(1)
                    params_str = func_match.group(2)
                    if params_str:
                        # Parse FastAPI parameters (including type hints)
                        parameters = [p.strip().split(':')[0].strip() for p in params_str.split(',') if p.strip()]
                
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method,
                    handler_name=handler_name,
                    file_path=str(file_path),
                    parameters=parameters,
                    decorators=[f'@app.{method.lower()}']
                ))
        
        return endpoints
    
    def _detect_django_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect Django endpoints from urls.py patterns"""
        endpoints = []
        
        # Django URL patterns
        url_pattern = r'path\([\'"]([^\'"]+)[\'"],\s*(\w+)(?:\.as_view\(\))?\s*(?:,\s*name\s*=\s*[\'"]([^\'"]+)[\'"])?\)'
        
        matches = re.finditer(url_pattern, content, re.MULTILINE)
        
        for match in matches:
            path = match.group(1)
            handler_name = match.group(2)
            name = match.group(3)
            
            # Django paths don't specify methods directly, assume common ones
            methods = ['GET', 'POST']  # Default assumption
            
            for method in methods:
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method,
                    handler_name=handler_name,
                    file_path=str(file_path),
                    decorators=['path()']
                ))
        
        return endpoints
    
    def _detect_starlette_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect Starlette endpoints"""
        endpoints = []
        
        # Starlette route patterns
        route_pattern = r'Route\([\'"]([^\'"]+)[\'"],\s*(\w+)(?:,\s*methods\s*=\s*\[([^\]]+)\])?\)'
        
        matches = re.finditer(route_pattern, content, re.MULTILINE)
        
        for match in matches:
            path = match.group(1)
            handler_name = match.group(2)
            methods_str = match.group(3)
            
            methods = ['GET']  # Default
            if methods_str:
                methods = [m.strip().strip('\'"') for m in methods_str.split(',')]
            
            for method in methods:
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method.upper(),
                    handler_name=handler_name,
                    file_path=str(file_path),
                    decorators=['Route()']
                ))
        
        return endpoints
    
    def _detect_tornado_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect Tornado endpoints from handler classes"""
        endpoints = []
        
        # Look for Tornado handler classes
        handler_pattern = r'class\s+(\w+)\s*\([^)]*RequestHandler[^)]*\):'
        
        matches = re.finditer(handler_pattern, content, re.MULTILINE)
        
        for match in matches:
            handler_name = match.group(1)
            
            # Look for HTTP method handlers in the class
            start_pos = match.end()
            class_content = self._extract_class_content(content, start_pos)
            
            method_patterns = ['get', 'post', 'put', 'delete', 'patch']
            
            for method in method_patterns:
                method_pattern = rf'def\s+{method}\s*\('
                if re.search(method_pattern, class_content):
                    endpoints.append(EndpointInfo(
                        path='/*',  # Tornado routing is configured elsewhere
                        method=method.upper(),
                        handler_name=handler_name,
                        file_path=str(file_path)
                    ))
        
        return endpoints
    
    def _detect_aiohttp_endpoints(self, content: str, file_path: Path) -> List[EndpointInfo]:
        """Detect aiohttp endpoints"""
        endpoints = []
        
        # aiohttp route decorators
        route_patterns = {
            'GET': r'@routes\.get\([\'"]([^\'"]+)[\'"]',
            'POST': r'@routes\.post\([\'"]([^\'"]+)[\'"]',
            'PUT': r'@routes\.put\([\'"]([^\'"]+)[\'"]',
            'DELETE': r'@routes\.delete\([\'"]([^\'"]+)[\'"]'
        }
        
        for method, pattern in route_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            
            for match in matches:
                path = match.group(1)
                
                # Find handler function
                start_pos = match.end()
                remaining_content = content[start_pos:]
                func_match = re.search(r'(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\):', remaining_content)
                
                handler_name = None
                parameters = []
                
                if func_match:
                    handler_name = func_match.group(1)
                    params_str = func_match.group(2)
                    if params_str:
                        parameters = [p.strip().split(':')[0].strip() for p in params_str.split(',') if p.strip()]
                
                endpoints.append(EndpointInfo(
                    path=path,
                    method=method,
                    handler_name=handler_name,
                    file_path=str(file_path),
                    parameters=parameters,
                    decorators=[f'@routes.{method.lower()}']
                ))
        
        return endpoints
    
    def _extract_class_content(self, content: str, start_pos: int) -> str:
        """Extract content of a class definition"""
        lines = content[start_pos:].split('\n')
        class_lines = []
        indent_level = None
        
        for line in lines:
            if line.strip() == '':
                class_lines.append(line)
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            if indent_level is None and line.strip():
                indent_level = current_indent
            
            if current_indent >= indent_level:
                class_lines.append(line)
            else:
                break
        
        return '\n'.join(class_lines)
    
    def detect_database_usage(self, file_path: Path) -> Optional[DatabaseInfo]:
        """Detect database usage in source file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Database detection patterns
            db_patterns = {
                'postgresql': [
                    r'import\s+psycopg2',
                    r'postgresql://',
                    r'from\s+sqlalchemy.*postgresql'
                ],
                'mysql': [
                    r'import\s+mysql',
                    r'mysql://',
                    r'pymysql',
                    r'MySQLdb'
                ],
                'sqlite': [
                    r'import\s+sqlite3',
                    r'sqlite://',
                    r'\.db$',
                    r'\.sqlite$'
                ],
                'mongodb': [
                    r'import\s+pymongo',
                    r'from\s+pymongo',
                    r'mongodb://',
                    r'MongoClient'
                ],
                'redis': [
                    r'import\s+redis',
                    r'redis://',
                    r'Redis\('
                ]
            }
            
            # ORM patterns
            orm_patterns = {
                'sqlalchemy': [r'from\s+sqlalchemy', r'import\s+sqlalchemy'],
                'django-orm': [r'from\s+django\.db', r'models\.Model'],
                'peewee': [r'import\s+peewee', r'from\s+peewee'],
                'tortoise': [r'from\s+tortoise', r'import\s+tortoise']
            }
            
            detected_dbs = []
            detected_orm = None
            
            # Check for database types
            for db_type, patterns in db_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                        detected_dbs.append(db_type)
                        break
            
            # Check for ORMs
            for orm, patterns in orm_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                        detected_orm = orm
                        break
                if detected_orm:
                    break
            
            if detected_dbs or detected_orm:
                return DatabaseInfo(
                    type=detected_dbs[0] if detected_dbs else 'unknown',
                    orm=detected_orm
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting database usage in {file_path}: {e}")
            return None
    
    def detect_deployment_config(self, project_path: Path) -> Optional[DeploymentInfo]:
        """Detect deployment configuration files"""
        deployment_info = DeploymentInfo()
        
        # Check for common deployment files
        deployment_files = {
            'Dockerfile': 'docker',
            'docker-compose.yml': 'docker',
            'docker-compose.yaml': 'docker',
            'Procfile': 'heroku',
            'app.yaml': 'gcp',
            'requirements.txt': 'python',
            'pyproject.toml': 'python',
            'setup.py': 'python',
            'kubernetes.yaml': 'kubernetes',
            'k8s.yaml': 'kubernetes'
        }
        
        config_files = []
        platform = None
        
        for file_name, detected_platform in deployment_files.items():
            file_path = project_path / file_name
            if file_path.exists():
                config_files.append(file_name)
                if not platform:  # Set first detected platform
                    platform = detected_platform
        
        if config_files:
            deployment_info.platform = platform
            deployment_info.config_files = config_files
            
            # Try to extract build/run commands from common files
            if 'Dockerfile' in config_files:
                deployment_info.build_commands = ['docker build -t app .']
                deployment_info.run_commands = ['docker run -p 8000:8000 app']
            elif 'Procfile' in config_files:
                try:
                    procfile_path = project_path / 'Procfile'
                    with open(procfile_path, 'r') as f:
                        content = f.read()
                        # Extract web process command
                        web_match = re.search(r'web:\s*(.+)', content)
                        if web_match:
                            deployment_info.run_commands = [web_match.group(1)]
                except Exception:
                    pass
            
            return deployment_info
        
        return None


# Utility functions for framework detection
def get_framework_by_name(name: str) -> Framework:
    """Get Framework enum by string name"""
    try:
        return Framework(name.lower())
    except ValueError:
        return Framework.UNKNOWN


def get_supported_frameworks() -> List[str]:
    """Get list of supported framework names"""
    return [f.value for f in Framework if f != Framework.UNKNOWN]


def is_web_framework(framework: Framework) -> bool:
    """Check if framework is a web framework"""
    web_frameworks = {
        Framework.FLASK, Framework.FASTAPI, Framework.DJANGO,
        Framework.STARLETTE, Framework.TORNADO, Framework.AIOHTTP,
        Framework.BOTTLE, Framework.CHERRYPY, Framework.PYRAMID,
        Framework.SANIC, Framework.QUART, Framework.EXPRESS
    }
    return framework in web_frameworks
