#!/usr/bin/env python3
"""
ProServe Instrumentation - Early Error Detection and Dynamic Logging
Integration with wmlog decorator system to prevent import/compatibility issues
"""

import inspect
import importlib
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import sys

# Always define fallback decorators first as a safety net
def log_execution(**kwargs):
    def decorator(func):
        return func
    return decorator

def log_imports(**kwargs):
    def decorator(func):
        return func
    return decorator

def log_errors(**kwargs):
    def decorator(func):
        return func
    return decorator

def log_compatibility(**kwargs):
    def decorator(func):
        return func
    return decorator

def log_context(operation_name):
    def decorator(func):
        return func
    return decorator

# Fallback classes
class WMLLogger:
    @staticmethod
    def get_logger(config=None, context=None):
        import logging
        return logging.getLogger("proserve-instrumentation")

class LoggingConfig:
    def __init__(self, **kwargs):
        pass

class LogContext:
    def __init__(self, **kwargs):
        pass

class DebugMode:
    @staticmethod
    def enable(level, filters):
        pass

# Try to import wmlog decorators and override fallbacks if available
WMLOG_AVAILABLE = False
try:
    from wmlog import WMLLogger as WMLLogger_Import
    WMLLogger = WMLLogger_Import
    WMLOG_AVAILABLE = True
    print("✅ wmlog WMLLogger available")
except ImportError:
    print("ℹ️ wmlog WMLLogger not available - using fallback")

# Try individual decorator imports
try:
    from wmlog import log_execution as log_execution_import
    log_execution = log_execution_import
    print("✅ wmlog log_execution available")
except ImportError:
    print("ℹ️ wmlog log_execution not available - using fallback")

try:
    from wmlog import log_imports as log_imports_import
    log_imports = log_imports_import
except ImportError:
    pass

try:
    from wmlog import log_errors as log_errors_import
    log_errors = log_errors_import
except ImportError:
    pass

try:
    from wmlog import log_compatibility as log_compatibility_import
    log_compatibility = log_compatibility_import
except ImportError:
    pass

try:
    from wmlog import log_context as log_context_import
    log_context = log_context_import
except ImportError:
    pass

try:
    from wmlog import DebugMode as DebugMode_import
    DebugMode = DebugMode_import
except ImportError:
    pass

try:
    from wmlog import LoggingConfig as LoggingConfig_import
    LoggingConfig = LoggingConfig_import
except ImportError:
    pass

try:
    from wmlog import LogContext as LogContext_import
    LogContext = LogContext_import
except ImportError:
    pass


class ProServeInstrumentation:
    """ProServe-specific instrumentation and early error detection"""
    
    def __init__(self, service_name: str = "proserve"):
        self.service_name = service_name
        self.logger = None
        self._setup_logger()
        
        # Track discovered issues
        self.compatibility_issues: List[Dict] = []
        self.import_failures: List[Dict] = []
        self.missing_aliases: List[Dict] = []
    
    def _setup_logger(self):
        """Setup wmlog logger for instrumentation"""
        if WMLOG_AVAILABLE:
            config = LoggingConfig(
                service_name=f"{self.service_name}-instrumentation",
                log_level="DEBUG",
                console_enabled=True
            )
            context = LogContext(
                service_name=f"{self.service_name}-instrumentation",
                custom_fields={"component": "instrumentation"}
            )
            self.logger = WMLLogger.get_logger(config, context)
    
    def enable_debug_mode(self, filters: Optional[List[str]] = None):
        """Enable wmlog debug mode for ProServe modules"""
        if WMLOG_AVAILABLE:
            proserve_filters = filters or ["proserve", "static", "manifest", "sdk"]
            DebugMode.enable("DEBUG", proserve_filters)
            if self.logger:
                self.logger.logger.info("Debug mode enabled", filters=proserve_filters)


def early_import_validator(required_modules: List[str]):
    """Decorator to validate imports before function execution"""
    def decorator(func: Callable) -> Callable:
        if not WMLOG_AVAILABLE:
            return func
            
        @log_imports(track_missing=True)
        @log_errors(include_traceback=True, reraise=True)
        def wrapper(*args, **kwargs):
            missing_modules = []
            
            for module_name in required_modules:
                try:
                    importlib.import_module(module_name)
                except ImportError as e:
                    missing_modules.append({
                        'module': module_name,
                        'error': str(e),
                        'function': func.__name__
                    })
            
            if missing_modules:
                # Log missing modules before execution
                config = LoggingConfig(
                    service_name="proserve-import-validator",
                    log_level="ERROR",
                    console_enabled=True
                )
                context = LogContext(
                    service_name="proserve-import-validator"
                )
                logger = WMLLogger.get_logger(config, context)
                logger.logger.error(
                    f"Missing required modules for {func.__name__}",
                    missing_modules=missing_modules,
                    function=func.__name__
                )
                
                # Optionally raise or continue with fallback
                raise ImportError(f"Required modules missing: {[m['module'] for m in missing_modules]}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def compatibility_checker(
    expected_attributes: Optional[List[str]] = None,
    expected_methods: Optional[List[str]] = None,
    fallback_on_missing: bool = False
):
    """Enhanced compatibility checker with early warning system"""
    def decorator(func: Callable) -> Callable:
        if not WMLOG_AVAILABLE:
            return func
            
        @log_compatibility(
            check_attributes=expected_attributes,
            check_methods=expected_methods
        )
        @log_execution(include_args=False, include_result=False)
        def wrapper(*args, **kwargs):
            # Check first argument (usually manifest, config object)
            if args and (expected_attributes or expected_methods):
                obj = args[0]
                obj_type = type(obj).__name__
                
                issues = []
                
                # Check attributes
                if expected_attributes:
                    for attr in expected_attributes:
                        if not hasattr(obj, attr):
                            issues.append({
                                'type': 'missing_attribute',
                                'name': attr,
                                'object_type': obj_type,
                                'function': func.__name__
                            })
                
                # Check methods
                if expected_methods:
                    for method in expected_methods:
                        if not hasattr(obj, method) or not callable(getattr(obj, method, None)):
                            issues.append({
                                'type': 'missing_method',
                                'name': method,
                                'object_type': obj_type,
                                'function': func.__name__
                            })
                
                if issues:
                    config = LoggingConfig(
                        service_name="proserve-compatibility",
                        log_level="WARNING",
                        console_enabled=True
                    )
                    context = LogContext(
                        service_name="proserve-compatibility"
                    )
                    logger = WMLLogger.get_logger(config, context)
                    logger.logger.warning(
                        f"Compatibility issues detected in {func.__name__}",
                        issues=issues,
                        object_type=obj_type,
                        fallback_enabled=fallback_on_missing
                    )
                    
                    if not fallback_on_missing:
                        # Create detailed error message
                        missing_attrs = [i['name'] for i in issues if i['type'] == 'missing_attribute']
                        missing_methods = [i['name'] for i in issues if i['type'] == 'missing_method']
                        
                        error_msg = f"Compatibility check failed for {obj_type} in {func.__name__}"
                        if missing_attrs:
                            error_msg += f"\nMissing attributes: {missing_attrs}"
                        if missing_methods:
                            error_msg += f"\nMissing methods: {missing_methods}"
                        
                        raise AttributeError(error_msg)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ProServe-specific decorator combinations
def instrument_manifest_handler(func: Callable) -> Callable:
    """Instrument manifest handling functions"""
    if not WMLOG_AVAILABLE:
        return func
        
    return compatibility_checker(
        expected_attributes=['name', 'version', 'type', 'port'],
        fallback_on_missing=False
    )(log_execution(
        level="DEBUG",
        include_args=True,
        include_result=False
    )(func))


def instrument_static_handler(func: Callable) -> Callable:
    """Instrument static file handling functions"""
    if not WMLOG_AVAILABLE:
        return func
        
    return compatibility_checker(
        expected_attributes=['static_hosting', 'static_dirs'],
        fallback_on_missing=True
    )(log_execution(
        level="INFO",
        include_timing=True
    )(func))


def instrument_sdk_imports(func: Callable) -> Callable:
    """Instrument SDK import-heavy functions"""
    if not WMLOG_AVAILABLE:
        return func
        
    return early_import_validator([
        'proserve.core',
        'proserve.sdk'
    ])(log_imports(
        track_missing=True,
        track_timing=True
    )(func))


class StaticHostingDiagnostics:
    """Specialized diagnostics for static hosting issues"""
    
    @staticmethod
    def diagnose_manifest(manifest) -> Dict[str, Any]:
        """Diagnose static hosting configuration in manifest"""
        diagnostics = {
            'status': 'unknown',
            'issues': [],
            'recommendations': []
        }
        
        # Check for static_hosting attribute
        if not hasattr(manifest, 'static_hosting'):
            diagnostics['issues'].append('No static_hosting attribute found')
            diagnostics['recommendations'].append('Add static_hosting configuration to manifest')
            diagnostics['status'] = 'misconfigured'
        else:
            static_config = manifest.static_hosting
            
            if not static_config:
                diagnostics['issues'].append('static_hosting is empty')
                diagnostics['recommendations'].append('Configure static_hosting with enabled: true')
            elif not static_config.get('enabled', True):
                diagnostics['issues'].append('static_hosting is disabled')
                diagnostics['recommendations'].append('Set static_hosting.enabled: true')
            else:
                static_dir = static_config.get('static_dir', '.')
                if not Path(static_dir).exists():
                    diagnostics['issues'].append(f'static_dir does not exist: {static_dir}')
                    diagnostics['recommendations'].append(f'Create directory {static_dir} or update static_dir path')
                
                diagnostics['status'] = 'ok' if not diagnostics['issues'] else 'issues_found'
        
        return diagnostics
    
    @staticmethod
    @log_execution(level="INFO", include_result=True)
    def log_static_routes(app) -> List[Dict]:
        """Log all registered static routes for debugging"""
        static_routes = []
        
        if hasattr(app, 'router') and hasattr(app.router, '_resources'):
            for resource in app.router._resources:
                if hasattr(resource, '_path') and 'static' in str(resource._path).lower():
                    static_routes.append({
                        'path': str(resource._path),
                        'name': getattr(resource, '_name', 'unnamed'),
                        'methods': list(resource._methods) if hasattr(resource, '_methods') else []
                    })
        
        return static_routes


# Export instrumentation functions
__all__ = [
    'ProServeInstrumentation',
    'early_import_validator', 
    'compatibility_checker',
    'instrument_manifest_handler',
    'instrument_static_handler', 
    'instrument_sdk_imports',
    'StaticHostingDiagnostics'
]
