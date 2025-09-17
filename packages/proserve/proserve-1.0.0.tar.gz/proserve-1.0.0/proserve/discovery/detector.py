"""
ProServe Service Detector
Advanced framework detection and service analysis tools
Ported from edpmt-framework with enhanced capabilities
"""

import os
import re
import ast
import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ServiceInfo:
    """Detected service information"""
    name: str
    framework: str
    version: Optional[str]
    path: Path
    entry_point: Optional[str]
    config_files: List[str]
    dependencies: List[str]
    endpoints: List[Dict[str, Any]]
    database_info: Optional[Dict[str, Any]]
    deployment_info: Optional[Dict[str, Any]]
    complexity_score: int
    migration_difficulty: str  # easy, medium, hard
    confidence_score: float  # 0.0 - 1.0


class ServiceDetector:
    """Advanced service detection and analysis"""
    
    def __init__(self):
        self.supported_frameworks = {
            'flask': {
                'patterns': [r'from\s+flask\s+import', r'Flask\(__name__\)'],
                'files': ['app.py', 'main.py', 'run.py', 'wsgi.py'],
                'config_files': ['config.py', 'settings.py', '.env', 'requirements.txt']
            },
            'fastapi': {
                'patterns': [r'from\s+fastapi\s+import', r'FastAPI\('],
                'files': ['main.py', 'app.py', 'api.py'],
                'config_files': ['requirements.txt', 'pyproject.toml', '.env']
            },
            'django': {
                'patterns': [r'from\s+django', r'DJANGO_SETTINGS_MODULE'],
                'files': ['manage.py', 'wsgi.py', 'asgi.py', 'settings.py'],
                'config_files': ['settings.py', 'requirements.txt', 'pyproject.toml']
            },
            'express': {
                'patterns': [r'require\([\'"]express[\'"\)', r'express\(\)'],
                'files': ['app.js', 'server.js', 'index.js', 'main.js'],
                'config_files': ['package.json', '.env', 'config.js']
            },
            'nestjs': {
                'patterns': [r'@nestjs/', r'NestFactory.create'],
                'files': ['main.ts', 'app.module.ts', 'bootstrap.ts'],
                'config_files': ['package.json', 'nest-cli.json', 'tsconfig.json']
            },
            'spring': {
                'patterns': [r'@SpringBootApplication', r'@RestController'],
                'files': ['Application.java', 'Main.java'],
                'config_files': ['pom.xml', 'build.gradle', 'application.properties', 'application.yml']
            },
            'aspnet': {
                'patterns': [r'using\s+Microsoft\.AspNetCore', r'WebApplication\.Create'],
                'files': ['Program.cs', 'Startup.cs'],
                'config_files': ['appsettings.json', '*.csproj', 'web.config']
            },
            'rails': {
                'patterns': [r'Rails\.application', r'class.*< ApplicationController'],
                'files': ['config.ru', 'application.rb'],
                'config_files': ['Gemfile', 'config/application.rb', 'config/routes.rb']
            },
            'go': {
                'patterns': [r'package\s+main', r'net/http', r'gin-gonic/gin'],
                'files': ['main.go', 'server.go', 'app.go'],
                'config_files': ['go.mod', 'go.sum', 'Dockerfile']
            },
            'phoenix': {
                'patterns': [r'defmodule.*Web', r'use Phoenix'],
                'files': ['mix.exs', 'endpoint.ex'],
                'config_files': ['mix.exs', 'config.exs', 'prod.exs']
            }
        }
        
        self.database_patterns = {
            'postgresql': [r'postgresql://', r'psycopg2', r'pg_dump'],
            'mysql': [r'mysql://', r'MySQLdb', r'pymysql'],
            'mongodb': [r'mongodb://', r'pymongo', r'mongoose'],
            'redis': [r'redis://', r'redis-py', r'ioredis'],
            'sqlite': [r'sqlite://', r'sqlite3', r'\.db$'],
            'elasticsearch': [r'elasticsearch', r'elastic-search']
        }
        
        self.deployment_patterns = {
            'docker': ['Dockerfile', 'docker-compose.yml', '.dockerignore'],
            'kubernetes': ['*.yaml', '*.yml', 'kustomization.yaml'],
            'heroku': ['Procfile', 'runtime.txt', 'app.json'],
            'aws': ['.aws/', 'serverless.yml', 'template.yaml'],
            'gcp': ['app.yaml', 'cloudbuild.yaml', '.gcloudignore'],
            'azure': ['azure-pipelines.yml', '.azure/']
        }

    def detect(self, path: Path) -> List[ServiceInfo]:
        """Detect all services in the given path"""
        services = []
        
        if not path.exists():
            logger.warning(f"Path does not exist: {path}")
            return services
        
        logger.info(f"Scanning for services in: {path}")
        
        # Scan for potential service directories
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                service_info = self._analyze_directory(item)
                if service_info:
                    services.append(service_info)
        
        # Also check the root directory itself
        root_service = self._analyze_directory(path)
        if root_service:
            services.append(root_service)
        
        logger.info(f"Found {len(services)} services")
        return services

    def _analyze_directory(self, dir_path: Path) -> Optional[ServiceInfo]:
        """Analyze a directory for service patterns"""
        
        try:
            # Get all files in directory (recursive)
            files = []
            for root, dirs, filenames in os.walk(dir_path):
                # Skip hidden directories and common non-service directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in ['node_modules', '__pycache__', 'venv', 'env', 'build', 'dist']]
                
                for filename in filenames:
                    file_path = Path(root) / filename
                    files.append(file_path)
            
            if not files:
                return None
            
            # Detect framework
            framework_info = self._detect_framework_in_files(files)
            if not framework_info:
                return None
            
            framework, confidence, entry_point = framework_info
            
            # Extract service information
            service_name = dir_path.name
            config_files = self._find_config_files(files, framework)
            dependencies = self._extract_dependencies(files, framework)
            endpoints = self._extract_endpoints(files, framework)
            database_info = self._detect_databases(files)
            deployment_info = self._detect_deployment(files)
            
            # Calculate complexity and migration difficulty
            complexity_score = self._calculate_complexity(files, framework, endpoints, dependencies)
            migration_difficulty = self._assess_migration_difficulty(complexity_score, framework, database_info)
            
            return ServiceInfo(
                name=service_name,
                framework=framework,
                version=self._extract_framework_version(files, framework),
                path=dir_path,
                entry_point=entry_point,
                config_files=config_files,
                dependencies=dependencies,
                endpoints=endpoints,
                database_info=database_info,
                deployment_info=deployment_info,
                complexity_score=complexity_score,
                migration_difficulty=migration_difficulty,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Error analyzing directory {dir_path}: {e}")
            return None

    def _detect_framework_in_files(self, files: List[Path]) -> Optional[Tuple[str, float, Optional[str]]]:
        """Detect framework from file analysis"""
        
        framework_scores = defaultdict(float)
        entry_points = {}
        
        for file_path in files:
            if file_path.suffix not in ['.py', '.js', '.ts', '.java', '.cs', '.rb', '.go', '.ex']:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for framework, info in self.supported_frameworks.items():
                    score = 0.0
                    
                    # Check patterns in content
                    for pattern in info['patterns']:
                        matches = len(re.findall(pattern, content, re.IGNORECASE))
                        score += matches * 0.3
                    
                    # Check if filename matches expected files
                    if file_path.name in info['files']:
                        score += 0.5
                        entry_points[framework] = str(file_path.relative_to(files[0].parent.parent))
                    
                    # Boost score for main entry files
                    if file_path.name in ['main.py', 'app.py', 'server.js', 'main.ts']:
                        score += 0.2
                    
                    framework_scores[framework] += score
                
            except Exception as e:
                logger.debug(f"Could not read file {file_path}: {e}")
                continue
        
        if not framework_scores:
            return None
        
        # Get the framework with highest score
        best_framework = max(framework_scores.items(), key=lambda x: x[1])
        framework, score = best_framework
        
        # Require minimum confidence
        if score < 0.5:
            return None
        
        # Normalize confidence score
        confidence = min(score / 2.0, 1.0)
        
        return framework, confidence, entry_points.get(framework)

    def _find_config_files(self, files: List[Path], framework: str) -> List[str]:
        """Find configuration files for the detected framework"""
        
        config_files = []
        expected_configs = self.supported_frameworks.get(framework, {}).get('config_files', [])
        
        for file_path in files:
            for config_pattern in expected_configs:
                if '*' in config_pattern:
                    # Handle glob patterns
                    import fnmatch
                    if fnmatch.fnmatch(file_path.name, config_pattern):
                        config_files.append(str(file_path.relative_to(files[0].parent.parent)))
                else:
                    if file_path.name == config_pattern:
                        config_files.append(str(file_path.relative_to(files[0].parent.parent)))
        
        return config_files

    def _extract_dependencies(self, files: List[Path], framework: str) -> List[str]:
        """Extract project dependencies"""
        
        dependencies = []
        
        for file_path in files:
            try:
                if file_path.name == 'requirements.txt':
                    content = file_path.read_text()
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before version specifier)
                            package = re.split(r'[>=<!=]', line)[0].strip()
                            dependencies.append(package)
                
                elif file_path.name == 'package.json':
                    content = file_path.read_text()
                    data = json.loads(content)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    dependencies.extend(list(deps.keys()))
                    dependencies.extend(list(dev_deps.keys()))
                
                elif file_path.name == 'Gemfile':
                    content = file_path.read_text()
                    for line in content.split('\n'):
                        match = re.search(r'gem\s+[\'"]([^\'"]+)[\'"]', line)
                        if match:
                            dependencies.append(match.group(1))
                
                elif file_path.name == 'go.mod':
                    content = file_path.read_text()
                    for line in content.split('\n'):
                        if line.strip().startswith('require'):
                            continue
                        match = re.search(r'^\s*([^\s]+)\s+v', line)
                        if match:
                            dependencies.append(match.group(1))
                            
            except Exception as e:
                logger.debug(f"Could not parse dependencies from {file_path}: {e}")
        
        return list(set(dependencies))  # Remove duplicates

    def _extract_endpoints(self, files: List[Path], framework: str) -> List[Dict[str, Any]]:
        """Extract API endpoints from source files"""
        
        endpoints = []
        
        for file_path in files:
            if file_path.suffix not in ['.py', '.js', '.ts', '.java', '.cs', '.rb', '.go']:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                if framework == 'flask':
                    endpoints.extend(self._extract_flask_endpoints(content, file_path))
                elif framework == 'fastapi':
                    endpoints.extend(self._extract_fastapi_endpoints(content, file_path))
                elif framework == 'django':
                    endpoints.extend(self._extract_django_endpoints(content, file_path))
                elif framework == 'express':
                    endpoints.extend(self._extract_express_endpoints(content, file_path))
                elif framework == 'spring':
                    endpoints.extend(self._extract_spring_endpoints(content, file_path))
                
            except Exception as e:
                logger.debug(f"Could not extract endpoints from {file_path}: {e}")
        
        return endpoints

    def _extract_flask_endpoints(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract Flask route definitions"""
        endpoints = []
        
        # Pattern for Flask routes: @app.route('/path', methods=['GET', 'POST'])
        route_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods\s*=\s*\[([^\]]+)\])?\)'
        
        for match in re.finditer(route_pattern, content):
            path = match.group(1)
            methods_str = match.group(2)
            methods = ['GET']  # Default
            
            if methods_str:
                methods = [m.strip().strip('\'"') for m in methods_str.split(',')]
            
            endpoints.append({
                'path': path,
                'methods': methods,
                'framework': 'flask',
                'file': str(file_path.name)
            })
        
        return endpoints

    def _extract_fastapi_endpoints(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract FastAPI endpoint definitions"""
        endpoints = []
        
        # Pattern for FastAPI routes: @app.get("/path"), @app.post("/path"), etc.
        route_pattern = r'@app\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]'
        
        for match in re.finditer(route_pattern, content):
            method = match.group(1).upper()
            path = match.group(2)
            
            endpoints.append({
                'path': path,
                'methods': [method],
                'framework': 'fastapi',
                'file': str(file_path.name)
            })
        
        return endpoints

    def _extract_django_endpoints(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract Django URL patterns"""
        endpoints = []
        
        if 'urlpatterns' in content or 'path(' in content:
            # Pattern for Django URLs: path('admin/', admin.site.urls)
            url_pattern = r'path\([\'"]([^\'"]+)[\'"]'
            
            for match in re.finditer(url_pattern, content):
                path = match.group(1)
                
                endpoints.append({
                    'path': f"/{path}",
                    'methods': ['GET'],  # Django routes can handle multiple methods
                    'framework': 'django',
                    'file': str(file_path.name)
                })
        
        return endpoints

    def _extract_express_endpoints(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract Express.js route definitions"""
        endpoints = []
        
        # Pattern for Express routes: app.get('/path', handler), router.post('/path', handler)
        route_pattern = r'(?:app|router)\.(get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"]'
        
        for match in re.finditer(route_pattern, content):
            method = match.group(1).upper()
            path = match.group(2)
            
            endpoints.append({
                'path': path,
                'methods': [method],
                'framework': 'express',
                'file': str(file_path.name)
            })
        
        return endpoints

    def _extract_spring_endpoints(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract Spring Boot endpoint definitions"""
        endpoints = []
        
        # Pattern for Spring annotations: @GetMapping("/path"), @PostMapping("/path"), etc.
        mapping_pattern = r'@(Get|Post|Put|Delete|Patch)Mapping\([\'"]([^\'"]+)[\'"]'
        
        for match in re.finditer(mapping_pattern, content):
            method = match.group(1).upper()
            path = match.group(2)
            
            endpoints.append({
                'path': path,
                'methods': [method],
                'framework': 'spring',
                'file': str(file_path.name)
            })
        
        # Also check for generic @RequestMapping
        request_mapping_pattern = r'@RequestMapping\([^)]*value\s*=\s*[\'"]([^\'"]+)[\'"][^)]*method\s*=\s*RequestMethod\.(\w+)'
        
        for match in re.finditer(request_mapping_pattern, content):
            path = match.group(1)
            method = match.group(2).upper()
            
            endpoints.append({
                'path': path,
                'methods': [method],
                'framework': 'spring',
                'file': str(file_path.name)
            })
        
        return endpoints

    def _detect_databases(self, files: List[Path]) -> Optional[Dict[str, Any]]:
        """Detect database usage in the project"""
        
        databases = []
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for db_type, patterns in self.database_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            if db_type not in databases:
                                databases.append(db_type)
                            break
                
            except Exception:
                continue
        
        if databases:
            return {
                'types': databases,
                'primary': databases[0] if databases else None,
                'detected_from': 'source_analysis'
            }
        
        return None

    def _detect_deployment(self, files: List[Path]) -> Optional[Dict[str, Any]]:
        """Detect deployment configuration"""
        
        deployment_types = []
        deployment_files = []
        
        for file_path in files:
            for deploy_type, patterns in self.deployment_patterns.items():
                for pattern in patterns:
                    if pattern.startswith('*'):
                        # Handle glob patterns
                        import fnmatch
                        if fnmatch.fnmatch(file_path.name, pattern):
                            deployment_types.append(deploy_type)
                            deployment_files.append(str(file_path.name))
                    else:
                        if file_path.name == pattern or pattern in str(file_path):
                            deployment_types.append(deploy_type)
                            deployment_files.append(str(file_path.name))
        
        if deployment_types:
            return {
                'types': list(set(deployment_types)),
                'files': deployment_files,
                'containerized': 'docker' in deployment_types,
                'orchestrated': 'kubernetes' in deployment_types
            }
        
        return None

    def _extract_framework_version(self, files: List[Path], framework: str) -> Optional[str]:
        """Extract framework version from dependency files"""
        
        for file_path in files:
            try:
                if file_path.name == 'requirements.txt':
                    content = file_path.read_text()
                    for line in content.split('\n'):
                        if framework.lower() in line.lower():
                            version_match = re.search(r'==([^\s]+)', line)
                            if version_match:
                                return version_match.group(1)
                            # Try >= or other operators
                            version_match = re.search(r'[>=<]+([^\s,]+)', line)
                            if version_match:
                                return f"~{version_match.group(1)}"
                
                elif file_path.name == 'package.json':
                    content = file_path.read_text()
                    data = json.loads(content)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    for dep, version in deps.items():
                        if framework.lower() in dep.lower():
                            return version.lstrip('^~>=<')
                            
            except Exception:
                continue
        
        return None

    def _calculate_complexity(self, files: List[Path], framework: str, 
                            endpoints: List[Dict], dependencies: List[str]) -> int:
        """Calculate service complexity score (0-100)"""
        
        score = 0
        
        # File count factor
        code_files = [f for f in files if f.suffix in ['.py', '.js', '.ts', '.java', '.cs', '.rb', '.go']]
        score += min(len(code_files) * 2, 30)
        
        # Endpoint count factor
        score += min(len(endpoints) * 3, 25)
        
        # Dependency count factor
        score += min(len(dependencies), 20)
        
        # Framework complexity factor
        framework_complexity = {
            'flask': 5, 'fastapi': 7, 'django': 15,
            'express': 8, 'nestjs': 12, 'spring': 18,
            'aspnet': 15, 'rails': 12, 'go': 6, 'phoenix': 10
        }
        score += framework_complexity.get(framework, 10)
        
        # Configuration file factor
        config_count = len([f for f in files if f.suffix in ['.yml', '.yaml', '.json', '.xml', '.properties']])
        score += min(config_count * 2, 10)
        
        return min(score, 100)

    def _assess_migration_difficulty(self, complexity_score: int, framework: str, 
                                   database_info: Optional[Dict]) -> str:
        """Assess migration difficulty based on various factors"""
        
        # Base difficulty from complexity
        if complexity_score < 30:
            base_difficulty = 1  # easy
        elif complexity_score < 60:
            base_difficulty = 2  # medium
        else:
            base_difficulty = 3  # hard
        
        # Framework-specific difficulty modifiers
        framework_difficulty = {
            'flask': 0, 'fastapi': 0, 'express': 0,
            'django': 1, 'spring': 2, 'aspnet': 2,
            'rails': 1, 'nestjs': 1, 'go': 0, 'phoenix': 1
        }
        base_difficulty += framework_difficulty.get(framework, 1)
        
        # Database complexity modifier
        if database_info:
            db_types = database_info.get('types', [])
            if len(db_types) > 1:
                base_difficulty += 1
            if any(db in ['mongodb', 'elasticsearch'] for db in db_types):
                base_difficulty += 1
        
        # Final difficulty assessment
        if base_difficulty <= 2:
            return 'easy'
        elif base_difficulty <= 4:
            return 'medium'
        else:
            return 'hard'


class FrameworkDetector:
    """Advanced framework detection with confidence scoring"""
    
    def __init__(self):
        self.service_detector = ServiceDetector()
    
    def detect_framework(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Detect web framework in file with detailed information"""
        
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check each supported framework
            for framework, info in self.service_detector.supported_frameworks.items():
                score = 0.0
                matches = []
                
                for pattern in info['patterns']:
                    pattern_matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if pattern_matches:
                        score += len(pattern_matches) * 0.3
                        matches.extend([m.group(0) for m in pattern_matches])
                
                if file_path.name in info['files']:
                    score += 0.7
                
                if score >= 0.5:
                    return {
                        'framework': framework,
                        'confidence': min(score, 1.0),
                        'matches': matches,
                        'file': str(file_path),
                        'expected_files': info['files'],
                        'config_files': info['config_files']
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting framework in {file_path}: {e}")
            return None


# Convenience functions for backward compatibility
def detect_service_framework(file_path: str) -> Optional[str]:
    """Detect service framework from file path"""
    detector = FrameworkDetector()
    result = detector.detect_framework(Path(file_path))
    return result['framework'] if result else None


def detect_services_in_directory(directory: str) -> List[Dict[str, Any]]:
    """Detect services in directory"""
    detector = ServiceDetector()
    services = detector.detect(Path(directory))
    return [asdict(service) for service in services]


def analyze_service_file(file_path: str) -> Dict[str, Any]:
    """Analyze single service file"""
    detector = FrameworkDetector()
    return detector.detect_framework(Path(file_path)) or {}
