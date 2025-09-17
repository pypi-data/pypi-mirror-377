"""
ProServe Helper Functions
Utility functions for ProServe framework operations
"""

import os
import re
import sys
import ast
import time
import uuid
import json
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import importlib.util

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def get_framework_info() -> Dict[str, Any]:
    """Get ProServe framework information"""
    return {
        'name': 'ProServe',
        'version': '1.0.0',
        'author': 'ProServe Development Team',
        'license': 'MIT',
        'url': 'https://github.com/proserve/proserve',
        'description': 'Professional Service Framework for Python',
        'features': [
            'Multi-platform service deployment',
            'MicroPython and Arduino support',
            'Service discovery and migration',
            'Advanced logging and monitoring',
            'Docker and container isolation',
            'WebSocket real-time communication',
            'Manifest-driven configuration',
            'CLI management tools'
        ],
        'environments': [
            'Linux (x86_64, ARM64)',
            'macOS (Intel, Apple Silicon)',
            'Windows (x86_64)',
            'MicroPython (RP2040, ESP32, ESP8266)',
            'Arduino (Uno, Nano, ESP32)',
            'Docker containers',
            'Kubernetes clusters'
        ],
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'platform': platform.platform(),
        'architecture': platform.machine(),
        'build_date': '2024-01-01'
    }


def validate_environment() -> Dict[str, Any]:
    """Validate ProServe environment and dependencies"""
    status = {
        'status': 'ok',
        'core_available': True,
        'python_version': sys.version_info[:3],
        'platform': platform.system(),
        'architecture': platform.machine(),
        'dependencies': {}
    }
    
    # Check core dependencies
    core_deps = [
        'aiohttp', 'yaml', 'structlog', 'asyncio', 'pathlib', 'dataclasses'
    ]
    
    for dep in core_deps:
        try:
            importlib.import_module(dep)
            status['dependencies'][dep] = True
        except ImportError:
            status['dependencies'][dep] = False
            if dep in ['aiohttp', 'yaml']:  # Critical dependencies
                status['status'] = 'error'
    
    # Check optional dependencies
    optional_deps = {
        'rich': 'Enhanced CLI output',
        'docker': 'Docker isolation support',
        'serial': 'Serial device communication',
        'psutil': 'System monitoring',
        'prometheus_client': 'Prometheus metrics',
        'dotenv': 'Environment file support'
    }
    
    for dep, description in optional_deps.items():
        try:
            importlib.import_module(dep)
            status['dependencies'][dep] = True
        except ImportError:
            status['dependencies'][dep] = False
    
    # Check embedded platform support
    status['micropython_available'] = check_micropython_support()
    status['arduino_available'] = check_arduino_support()
    status['serial_available'] = SERIAL_AVAILABLE
    status['psutil_available'] = PSUTIL_AVAILABLE
    
    return status


def detect_service_framework(file_path: Union[str, Path]) -> Optional[str]:
    """Detect web framework used in Python service file"""
    file_path = Path(file_path)
    
    if not file_path.exists() or not file_path.suffix == '.py':
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST to detect imports and framework patterns
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Framework detection patterns
        framework_patterns = {
            'flask': ['flask', 'Flask', '@app.route'],
            'fastapi': ['fastapi', 'FastAPI', '@app.get', '@app.post'],
            'django': ['django', 'from django', 'urls.py', 'models.py'],
            'aiohttp': ['aiohttp', 'web.Application', 'web.get', 'web.post'],
            'tornado': ['tornado', 'RequestHandler', 'Application'],
            'bottle': ['bottle', '@route', 'run('],
            'starlette': ['starlette', 'Starlette'],
            'quart': ['quart', 'Quart'],
            'sanic': ['sanic', 'Sanic']
        }
        
        # Check imports
        for framework, patterns in framework_patterns.items():
            for pattern in patterns:
                if any(pattern in imp for imp in imports):
                    return framework
        
        # Check content patterns
        for framework, patterns in framework_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    return framework
        
        return None
        
    except Exception:
        return None


def generate_service_id() -> str:
    """Generate unique service ID"""
    return f"proserve-{uuid.uuid4().hex[:8]}"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"


def sanitize_service_name(name: str) -> str:
    """Sanitize service name for use in filenames and identifiers"""
    # Remove special characters and replace with hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
    # Remove multiple consecutive hyphens
    sanitized = re.sub(r'-+', '-', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    # Convert to lowercase
    return sanitized.lower()


def get_platform_info() -> Dict[str, Any]:
    """Get detailed platform information"""
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'architecture': platform.architecture(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'is_embedded': False,
        'embedded_type': None
    }
    
    # Detect embedded platforms
    if 'micropython' in sys.implementation.name.lower():
        info['is_embedded'] = True
        info['embedded_type'] = 'micropython'
        info['board'] = detect_micropython_board()
    elif hasattr(sys, 'platform') and 'arduino' in sys.platform.lower():
        info['is_embedded'] = True
        info['embedded_type'] = 'arduino'
        info['board'] = detect_arduino_board()
    
    # Add system resources if available
    if PSUTIL_AVAILABLE:
        info.update({
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'disk_usage': psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:').total,
            'boot_time': psutil.boot_time()
        })
    
    return info


def detect_devices() -> List[Dict[str, Any]]:
    """Detect connected devices (USB, serial, etc.)"""
    devices = []
    
    if not SERIAL_AVAILABLE:
        return devices
    
    try:
        # Detect serial ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            device_info = {
                'type': 'serial',
                'port': port.device,
                'description': port.description,
                'hwid': port.hwid,
                'vid': getattr(port, 'vid', None),
                'pid': getattr(port, 'pid', None),
                'serial_number': getattr(port, 'serial_number', None),
                'manufacturer': getattr(port, 'manufacturer', None),
                'product': getattr(port, 'product', None),
                'platform': None,
                'board': None
            }
            
            # Detect platform and board based on VID/PID
            platform, board = detect_device_platform(device_info)
            device_info['platform'] = platform
            device_info['board'] = board
            
            devices.append(device_info)
    
    except Exception as e:
        pass
    
    return devices


def detect_device_platform(device_info: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Detect platform and board from device information"""
    vid = device_info.get('vid')
    pid = device_info.get('pid')
    description = device_info.get('description', '').lower()
    
    # Known VID/PID mappings for embedded platforms
    device_mappings = {
        # Raspberry Pi Pico (RP2040)
        (0x2E8A, 0x0005): ('rp2040', 'pico'),
        (0x2E8A, 0x000A): ('rp2040', 'pico-w'),
        
        # ESP32 devices
        (0x10C4, 0xEA60): ('esp32', 'esp32-devkit'),
        (0x1A86, 0x7523): ('esp32', 'esp32-generic'),
        (0x0403, 0x6001): ('esp32', 'esp32-ftdi'),
        
        # Arduino devices
        (0x2341, 0x0043): ('arduino', 'uno-r3'),
        (0x2341, 0x0001): ('arduino', 'uno'),
        (0x2341, 0x8036): ('arduino', 'leonardo'),
        (0x2341, 0x0036): ('arduino', 'leonardo'),
        (0x2341, 0x804D): ('arduino', 'zero'),
        (0x1B4F, 0x9206): ('arduino', 'nano'),
        
        # ESP8266 devices
        (0x10C4, 0xEA60): ('esp8266', 'nodemcu'),
        (0x1A86, 0x7523): ('esp8266', 'wemos-d1'),
    }
    
    # Check VID/PID mapping
    if vid and pid:
        mapping = device_mappings.get((vid, pid))
        if mapping:
            return mapping
    
    # Check description patterns
    description_patterns = {
        'pico': ('rp2040', 'pico'),
        'raspberry pi pico': ('rp2040', 'pico'),
        'esp32': ('esp32', 'esp32-generic'),
        'esp8266': ('esp8266', 'esp8266-generic'),
        'arduino uno': ('arduino', 'uno'),
        'arduino nano': ('arduino', 'nano'),
        'arduino leonardo': ('arduino', 'leonardo'),
        'nodemcu': ('esp8266', 'nodemcu'),
        'wemos': ('esp8266', 'wemos-d1')
    }
    
    for pattern, (platform, board) in description_patterns.items():
        if pattern in description:
            return platform, board
    
    return None, None


def is_embedded_platform(platform_name: str) -> bool:
    """Check if platform is an embedded platform"""
    embedded_platforms = [
        'rp2040', 'esp32', 'esp8266', 
        'arduino-uno', 'arduino-nano', 'arduino-leonardo',
        'micropython', 'circuitpython'
    ]
    return platform_name.lower() in embedded_platforms


def get_available_ports() -> List[int]:
    """Get list of available network ports"""
    available_ports = []
    
    # Common port ranges to check
    port_ranges = [
        (8000, 8100),  # Development ports
        (3000, 3010),  # Node.js common ports
        (5000, 5010),  # Flask common ports
        (9000, 9010)   # Various services
    ]
    
    if PSUTIL_AVAILABLE:
        # Get currently used ports
        used_ports = set()
        for conn in psutil.net_connections():
            if conn.laddr:
                used_ports.add(conn.laddr.port)
        
        # Check ranges for available ports
        for start, end in port_ranges:
            for port in range(start, end + 1):
                if port not in used_ports:
                    available_ports.append(port)
    else:
        # Fallback: suggest common development ports
        suggested_ports = [8000, 8080, 3000, 5000, 9000]
        available_ports.extend(suggested_ports)
    
    return sorted(available_ports)


def check_micropython_support() -> bool:
    """Check if MicroPython support is available"""
    try:
        # Check for common MicroPython tools
        tools = ['ampy', 'rshell', 'mpremote']
        for tool in tools:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                return True
        
        # Check for Python packages
        packages = ['ampy', 'adafruit-ampy', 'mpremote']
        for package in packages:
            try:
                importlib.import_module(package)
                return True
            except ImportError:
                continue
        
        return False
    except Exception:
        return False


def check_arduino_support() -> bool:
    """Check if Arduino support is available"""
    try:
        # Check for Arduino CLI
        result = subprocess.run(['arduino-cli', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        
        # Check for PlatformIO
        result = subprocess.run(['pio', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        
        return False
    except Exception:
        return False


def detect_micropython_board() -> Optional[str]:
    """Detect MicroPython board type"""
    try:
        # This would typically require connection to the device
        # For now, return None - can be enhanced with device communication
        return None
    except Exception:
        return None


def detect_arduino_board() -> Optional[str]:
    """Detect Arduino board type"""
    try:
        # This would typically require Arduino CLI or similar tool
        # For now, return None - can be enhanced with tool integration
        return None
    except Exception:
        return None


def find_free_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find a free network port starting from start_port"""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"Could not find free port in range {start_port}-{start_port + max_attempts}")


def validate_manifest_path(path: Union[str, Path]) -> Path:
    """Validate and normalize manifest file path"""
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")
    
    if path.suffix.lower() not in ['.yml', '.yaml']:
        raise ValueError(f"Invalid manifest file extension: {path.suffix}")
    
    return path.resolve()


def create_backup(source_path: Union[str, Path], backup_dir: Union[str, Path]) -> Path:
    """Create backup of file or directory"""
    import shutil
    
    source_path = Path(source_path)
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source_path.name}_{timestamp}"
    backup_path = backup_dir / backup_name
    
    if source_path.is_file():
        shutil.copy2(source_path, backup_path)
    elif source_path.is_dir():
        shutil.copytree(source_path, backup_path)
    else:
        raise ValueError(f"Source path does not exist: {source_path}")
    
    return backup_path


def load_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON file with error handling"""
    file_path = Path(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {file_path}: {e}")


def save_json_file(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2):
    """Save data to JSON file"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def measure_execution_time(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {format_duration(execution_time)}")
        return result
    return wrapper


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function on failure"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise e
                    
                    print(f"Attempt {attempt} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
        
        return wrapper
    return decorator


def normalize_path(path: Union[str, Path], relative_to: Optional[Path] = None) -> Path:
    """Normalize and resolve file path"""
    path = Path(path)
    
    if relative_to:
        if not path.is_absolute():
            path = relative_to / path
    
    return path.resolve()


def get_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
    """Get file hash using specified algorithm"""
    import hashlib
    
    file_path = Path(file_path)
    hash_obj = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def safe_import(module_name: str, package: Optional[str] = None) -> Optional[object]:
    """Safely import module without raising exception"""
    try:
        if package:
            return importlib.import_module(module_name, package)
        else:
            return importlib.import_module(module_name)
    except ImportError:
        return None
