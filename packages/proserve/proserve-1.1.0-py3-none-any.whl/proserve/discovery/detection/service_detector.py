"""
ProServe Service Detector - Main Service Detection Engine
Coordinates framework detection, endpoint analysis, and service information gathering
"""

import os
import time
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import structlog

from .service_models import (
    ServiceInfo, DetectionResult, Framework, EndpointInfo, 
    create_basic_service_info, merge_service_info
)
from .framework_detector import FrameworkDetector


logger = structlog.get_logger(__name__)


class ServiceDetector:
    """Advanced service detection and analysis"""
    
    def __init__(self):
        self.framework_detector = FrameworkDetector()
        
        # File patterns to scan for different languages
        self.scan_patterns = {
            'python': ['*.py'],
            'javascript': ['*.js', '*.ts'],
            'java': ['*.java'],
            'go': ['*.go'],
            'rust': ['*.rs']
        }
        
        # Files to prioritize during detection
        self.priority_files = [
            'main.py', 'app.py', 'run.py', 'server.py', 'wsgi.py', 'asgi.py',
            'manage.py', 'urls.py', 'views.py', 'api.py',
            'index.js', 'server.js', 'app.js', 'main.js',
            'Main.java', 'Application.java',
            'main.go', 'server.go',
            'main.rs', 'lib.rs'
        ]
        
        # Directories to ignore during scanning
        self.ignore_dirs = {
            '__pycache__', '.git', '.svn', 'node_modules', 'venv', 'env',
            '.venv', 'build', 'dist', 'target', '.pytest_cache', '.mypy_cache',
            '.tox', 'htmlcov', 'coverage', '.coverage', '.idea', '.vscode'
        }
    
    def detect_services_in_directory(self, directory: Path, 
                                   recursive: bool = True,
                                   max_depth: int = 5) -> DetectionResult:
        """Detect all services in a directory"""
        start_time = time.time()
        result = DetectionResult()
        
        if not directory.exists():
            result.add_error(f"Directory does not exist: {directory}")
            return result
        
        logger.info(f"Starting service detection in {directory}")
        
        try:
            # Find all relevant files
            files_to_scan = self._find_files_to_scan(directory, recursive, max_depth)
            result.total_files_scanned = len(files_to_scan)
            
            # Group files by potential projects
            project_groups = self._group_files_by_project(files_to_scan)
            
            # Analyze each project group
            for project_path, project_files in project_groups.items():
                try:
                    service = self._analyze_project(project_path, project_files)
                    if service and service.confidence_score > 0.3:  # Minimum confidence threshold
                        result.add_service(service)
                except Exception as e:
                    result.add_error(f"Error analyzing project at {project_path}: {e}")
                    logger.error(f"Error analyzing project {project_path}: {e}")
            
            result.detection_time = time.time() - start_time
            
            logger.info(f"Detection completed: {len(result.services)} services found in {result.detection_time:.2f}s")
            
        except Exception as e:
            result.add_error(f"Detection failed: {e}")
            logger.error(f"Service detection failed: {e}")
        
        return result
    
    def analyze_single_service(self, service_path: Path) -> Optional[ServiceInfo]:
        """Analyze a single service directory or file"""
        try:
            if service_path.is_file():
                # Single file analysis
                return self._analyze_single_file(service_path)
            elif service_path.is_dir():
                # Directory analysis
                files_to_scan = self._find_files_to_scan(service_path, recursive=True, max_depth=3)
                if files_to_scan:
                    return self._analyze_project(service_path, files_to_scan)
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing service at {service_path}: {e}")
            return None
    
    def _find_files_to_scan(self, directory: Path, recursive: bool, max_depth: int) -> List[Path]:
        """Find all files that should be scanned for service detection"""
        files_to_scan = []
        
        def scan_directory(dir_path: Path, current_depth: int):
            if current_depth > max_depth:
                return
            
            try:
                for item in dir_path.iterdir():
                    if item.is_file():
                        if self._should_scan_file(item):
                            files_to_scan.append(item)
                    elif item.is_dir() and recursive:
                        if item.name not in self.ignore_dirs:
                            scan_directory(item, current_depth + 1)
            except PermissionError:
                logger.warning(f"Permission denied accessing {dir_path}")
        
        scan_directory(directory, 0)
        
        # Sort by priority (priority files first)
        def file_priority(file_path: Path) -> int:
            if file_path.name in self.priority_files:
                return self.priority_files.index(file_path.name)
            return len(self.priority_files)
        
        files_to_scan.sort(key=file_priority)
        
        return files_to_scan
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Determine if a file should be scanned"""
        # Check file extensions
        for patterns in self.scan_patterns.values():
            for pattern in patterns:
                if file_path.match(pattern):
                    return True
        
        # Check priority files
        if file_path.name in self.priority_files:
            return True
        
        return False
    
    def _group_files_by_project(self, files: List[Path]) -> Dict[Path, List[Path]]:
        """Group files by their likely project directories"""
        projects = {}
        
        for file_path in files:
            project_root = self._find_project_root(file_path)
            if project_root not in projects:
                projects[project_root] = []
            projects[project_root].append(file_path)
        
        return projects
    
    def _find_project_root(self, file_path: Path) -> Path:
        """Find the likely project root for a file"""
        current_dir = file_path.parent
        
        # Look for common project indicators
        project_indicators = [
            'setup.py', 'pyproject.toml', 'requirements.txt', 'Pipfile',
            'package.json', 'yarn.lock', 'package-lock.json',
            'pom.xml', 'build.gradle', 'Cargo.toml', 'go.mod',
            'Dockerfile', 'docker-compose.yml', '.git'
        ]
        
        # Start from file directory and go up
        while current_dir.parent != current_dir:  # Stop at root
            # Check if this directory has project indicators
            for indicator in project_indicators:
                if (current_dir / indicator).exists():
                    return current_dir
            
            current_dir = current_dir.parent
        
        # If no project root found, use the file's directory
        return file_path.parent
    
    def _analyze_project(self, project_path: Path, project_files: List[Path]) -> Optional[ServiceInfo]:
        """Analyze a group of files as a project"""
        if not project_files:
            return None
        
        logger.debug(f"Analyzing project at {project_path} with {len(project_files)} files")
        
        # Find the most likely main file
        main_file = self._find_main_file(project_files)
        if not main_file:
            return None
        
        # Detect framework from main file
        framework, confidence = self.framework_detector.detect_framework(main_file)
        
        if framework == Framework.UNKNOWN:
            # Try other files if main file detection failed
            for file_path in project_files[:5]:  # Limit to avoid excessive processing
                framework, file_confidence = self.framework_detector.detect_framework(file_path)
                if framework != Framework.UNKNOWN:
                    confidence = file_confidence
                    main_file = file_path
                    break
        
        if framework == Framework.UNKNOWN:
            return None
        
        # Create basic service info
        service_name = self._extract_service_name(project_path, main_file)
        service = create_basic_service_info(service_name, framework.value, project_path)
        service.confidence_score = confidence
        service.entry_point = str(main_file.relative_to(project_path))
        
        # Detect endpoints
        all_endpoints = []
        for file_path in project_files:
            endpoints = self.framework_detector.detect_endpoints_in_file(file_path, framework)
            all_endpoints.extend(endpoints)
        
        service.endpoints = all_endpoints
        
        # Calculate complexity
        service.complexity_score = service.calculate_api_complexity()
        
        # Detect database usage
        for file_path in project_files:
            db_info = self.framework_detector.detect_database_usage(file_path)
            if db_info:
                service.database_info = db_info
                break
        
        # Detect deployment configuration
        deployment_info = self.framework_detector.detect_deployment_config(project_path)
        if deployment_info:
            service.deployment_info = deployment_info
        
        # Find configuration files
        service.config_files = self._find_config_files(project_path)
        
        # Extract dependencies
        service.dependencies = self._extract_dependencies(project_path)
        
        # Determine migration difficulty
        service.migration_difficulty = self._assess_migration_difficulty(service)
        
        logger.debug(f"Detected {framework.value} service '{service_name}' with {len(all_endpoints)} endpoints")
        
        return service
    
    def _analyze_single_file(self, file_path: Path) -> Optional[ServiceInfo]:
        """Analyze a single file for service information"""
        framework, confidence = self.framework_detector.detect_framework(file_path)
        
        if framework == Framework.UNKNOWN or confidence < 0.5:
            return None
        
        service_name = self._extract_service_name(file_path.parent, file_path)
        service = create_basic_service_info(service_name, framework.value, file_path.parent)
        service.confidence_score = confidence
        service.entry_point = file_path.name
        
        # Detect endpoints
        service.endpoints = self.framework_detector.detect_endpoints_in_file(file_path, framework)
        service.complexity_score = service.calculate_api_complexity()
        
        # Detect database usage
        service.database_info = self.framework_detector.detect_database_usage(file_path)
        
        return service
    
    def _find_main_file(self, project_files: List[Path]) -> Optional[Path]:
        """Find the most likely main/entry point file"""
        # Check for priority files first
        for priority_file in self.priority_files:
            for file_path in project_files:
                if file_path.name == priority_file:
                    return file_path
        
        # If no priority file found, return the first Python file
        for file_path in project_files:
            if file_path.suffix == '.py':
                return file_path
        
        # Fallback to first file
        return project_files[0] if project_files else None
    
    def _extract_service_name(self, project_path: Path, main_file: Path) -> str:
        """Extract a service name from project structure"""
        # Try project directory name first
        if project_path.name and project_path.name not in ['.', '..']:
            return project_path.name
        
        # Try main file name without extension
        if main_file:
            return main_file.stem
        
        return 'unknown-service'
    
    def _find_config_files(self, project_path: Path) -> List[str]:
        """Find configuration files in the project"""
        config_files = []
        
        common_config_files = [
            'config.py', 'settings.py', 'local_settings.py', 'production.py',
            '.env', '.env.local', '.env.production',
            'config.json', 'config.yaml', 'config.yml',
            'requirements.txt', 'Pipfile', 'pyproject.toml', 'setup.py'
        ]
        
        for config_file in common_config_files:
            if (project_path / config_file).exists():
                config_files.append(config_file)
        
        return config_files
    
    def _extract_dependencies(self, project_path: Path) -> List[str]:
        """Extract dependencies from project files"""
        dependencies = []
        
        # Check requirements.txt
        req_file = project_path / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before version specifier)
                            package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                            if package:
                                dependencies.append(package)
            except Exception as e:
                logger.warning(f"Error reading requirements.txt: {e}")
        
        # Check pyproject.toml
        pyproject_file = project_path / 'pyproject.toml'
        if pyproject_file.exists():
            try:
                import tomllib
                with open(pyproject_file, 'rb') as f:
                    data = tomllib.load(f)
                    
                # Extract dependencies from different sections
                for section in ['dependencies', 'tool.poetry.dependencies']:
                    deps = data
                    for key in section.split('.'):
                        deps = deps.get(key, {})
                    
                    if isinstance(deps, list):
                        dependencies.extend(deps)
                    elif isinstance(deps, dict):
                        dependencies.extend(deps.keys())
                        
            except Exception as e:
                logger.warning(f"Error reading pyproject.toml: {e}")
        
        return list(set(dependencies))  # Remove duplicates
    
    def _assess_migration_difficulty(self, service: ServiceInfo) -> str:
        """Assess migration difficulty based on service characteristics"""
        difficulty_score = 0
        
        # Framework complexity
        if service.framework == Framework.DJANGO:
            difficulty_score += 3
        elif service.framework == Framework.TORNADO:
            difficulty_score += 2
        elif service.framework in [Framework.FLASK, Framework.FASTAPI]:
            difficulty_score += 1
        
        # Number of endpoints
        if len(service.endpoints) > 50:
            difficulty_score += 3
        elif len(service.endpoints) > 20:
            difficulty_score += 2
        elif len(service.endpoints) > 10:
            difficulty_score += 1
        
        # Database complexity
        if service.database_info:
            if service.database_info.orm == 'django-orm':
                difficulty_score += 2
            elif service.database_info.orm:
                difficulty_score += 1
        
        # Dependencies
        if len(service.dependencies) > 30:
            difficulty_score += 2
        elif len(service.dependencies) > 15:
            difficulty_score += 1
        
        # Convert score to difficulty level
        if difficulty_score >= 7:
            return 'very_hard'
        elif difficulty_score >= 5:
            return 'hard'
        elif difficulty_score >= 3:
            return 'medium'
        else:
            return 'easy'


# Utility functions for service detection
def detect_service_framework(file_path: str) -> Dict[str, Any]:
    """Detect service framework from file path (backward compatibility)"""
    detector = ServiceDetector()
    service = detector.analyze_single_service(Path(file_path))
    
    if service:
        return {
            'framework': service.framework.value,
            'confidence': service.confidence_score,
            'endpoints': len(service.endpoints)
        }
    
    return {'framework': 'unknown', 'confidence': 0.0, 'endpoints': 0}


def detect_services_in_directory(directory: str) -> List[Dict[str, Any]]:
    """Detect services in directory (backward compatibility)"""
    detector = ServiceDetector()
    result = detector.detect_services_in_directory(Path(directory))
    
    return [service.to_dict() for service in result.services]


def analyze_service_file(file_path: str) -> Dict[str, Any]:
    """Analyze single service file (backward compatibility)"""
    detector = ServiceDetector()
    service = detector.analyze_single_service(Path(file_path))
    
    return service.to_dict() if service else {}


def create_service_detector() -> ServiceDetector:
    """Create a new service detector instance"""
    return ServiceDetector()
