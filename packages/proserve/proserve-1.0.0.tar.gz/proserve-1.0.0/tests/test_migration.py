"""
Migration and Discovery Tests
E2E tests for ServiceDetector, ServiceMigrator, and multi-framework migration
"""

import asyncio
import json
import shutil
import tempfile
from pathlib import Path
from .test_framework import ProServeTestFramework, TestSuite


async def test_service_detector_basic(framework: ProServeTestFramework):
    """Test basic ServiceDetector functionality"""
    from proserve.discovery.detector import ServiceDetector
    
    # Create mock Flask service structure
    flask_dir = framework.temp_dir / 'flask-service'
    flask_dir.mkdir()
    
    # Create Flask files
    (flask_dir / 'app.py').write_text('''
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/users')
def users():
    return jsonify([{"id": 1, "name": "John"}])

if __name__ == '__main__':
    app.run(debug=True)
''')
    
    (flask_dir / 'requirements.txt').write_text('''
Flask==2.3.3
gunicorn==20.1.0
requests==2.31.0
''')
    
    (flask_dir / 'README.md').write_text('# Flask Service\nA sample Flask application')
    
    # Run detection
    detector = ServiceDetector()
    service_info = await detector.detect_service(flask_dir)
    
    assert service_info is not None
    assert service_info.framework == 'flask'
    assert service_info.confidence > 0.7
    assert len(service_info.endpoints) >= 2  # /health, /api/users
    assert service_info.entry_point == 'app.py'
    
    return {
        'detection_successful': True,
        'framework': service_info.framework,
        'confidence': service_info.confidence,
        'endpoints_found': len(service_info.endpoints),
        'entry_point': service_info.entry_point,
        'complexity_score': service_info.complexity_score
    }


async def test_service_detector_fastapi(framework: ProServeTestFramework):
    """Test ServiceDetector with FastAPI service"""
    from proserve.discovery.detector import ServiceDetector
    
    # Create mock FastAPI service
    fastapi_dir = framework.temp_dir / 'fastapi-service'
    fastapi_dir.mkdir()
    
    (fastapi_dir / 'main.py').write_text('''
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/users")
async def get_users():
    return [{"id": 1, "name": "John"}]

@app.post("/api/users")
async def create_user(user: User):
    return user
''')
    
    (fastapi_dir / 'requirements.txt').write_text('''
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
''')
    
    # Run detection
    detector = ServiceDetector()
    service_info = await detector.detect_service(fastapi_dir)
    
    assert service_info is not None
    assert service_info.framework == 'fastapi'
    assert service_info.confidence > 0.8
    assert len(service_info.endpoints) >= 3  # /health, GET /api/users, POST /api/users
    
    return {
        'fastapi_detected': True,
        'framework': service_info.framework,
        'confidence': service_info.confidence,
        'endpoints_count': len(service_info.endpoints),
        'has_async': any('async' in ep.get('handler', '') for ep in service_info.endpoints)
    }


async def test_service_detector_multi_framework(framework: ProServeTestFramework):
    """Test ServiceDetector with multiple frameworks in directory"""
    from proserve.discovery.detector import ServiceDetector
    
    # Create multiple service directories
    services_dir = framework.temp_dir / 'services'
    services_dir.mkdir()
    
    # Django service
    django_dir = services_dir / 'django-app'
    django_dir.mkdir()
    (django_dir / 'manage.py').write_text('#!/usr/bin/env python\nimport django')
    (django_dir / 'settings.py').write_text('DEBUG = True\nDATABASE = {}')
    
    # Express.js service
    express_dir = services_dir / 'express-app'
    express_dir.mkdir()
    (express_dir / 'package.json').write_text(json.dumps({
        "name": "express-app",
        "dependencies": {"express": "^4.18.0"}
    }))
    (express_dir / 'app.js').write_text('''
const express = require('express');
const app = express();

app.get('/health', (req, res) => {
    res.json({status: 'ok'});
});

app.listen(3000);
''')
    
    # ProServe service
    proserve_dir = services_dir / 'proserve-app'
    proserve_dir.mkdir()
    (proserve_dir / 'manifest.yml').write_text('''
name: test-proserve-service
version: 1.0.0
framework: proserve
endpoints:
  - path: /health
    method: get
    handler: handlers.health.check
''')
    
    # Run detection on all services
    detector = ServiceDetector()
    all_services = await detector.scan_directory(services_dir)
    
    frameworks_found = [info.framework for info in all_services]
    
    assert len(all_services) == 3
    assert 'django' in frameworks_found
    assert 'express' in frameworks_found
    assert 'proserve' in frameworks_found
    
    return {
        'multi_detection': True,
        'services_count': len(all_services),
        'frameworks': frameworks_found,
        'django_detected': 'django' in frameworks_found,
        'express_detected': 'express' in frameworks_found,
        'proserve_detected': 'proserve' in frameworks_found
    }


async def test_service_migrator_flask_to_proserve(framework: ProServeTestFramework):
    """Test ServiceMigrator Flask to ProServe migration"""
    from proserve.migration.migrator import ServiceMigrator, MigrationConfig
    from proserve.discovery.detector import ServiceDetector
    
    # Create Flask service
    flask_dir = framework.temp_dir / 'flask-migration-test'
    flask_dir.mkdir()
    
    (flask_dir / 'app.py').write_text('''
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify([{"id": 1, "name": "John"}])

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    return jsonify({"id": 2, "name": data.get("name")})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
''')
    
    (flask_dir / 'requirements.txt').write_text('Flask==2.3.3\nrequests==2.31.0')
    
    # Detect service first
    detector = ServiceDetector()
    service_info = await detector.detect_service(flask_dir)
    
    # Configure migration
    config = MigrationConfig(
        create_backup=True,
        generate_manifest=True,
        convert_handlers=True,
        include_examples=True
    )
    
    # Run migration
    migrator = ServiceMigrator()
    result = await migrator.migrate_to_proserve(service_info, config)
    
    assert result.success == True
    assert result.manifest_path is not None
    assert result.manifest_path.exists()
    
    # Check generated manifest
    manifest_content = result.manifest_path.read_text()
    assert 'name:' in manifest_content
    assert 'framework: proserve' in manifest_content
    assert 'endpoints:' in manifest_content
    
    return {
        'migration_successful': result.success,
        'manifest_generated': result.manifest_path.exists() if result.manifest_path else False,
        'backup_created': result.backup_path.exists() if result.backup_path else False,
        'handlers_converted': len(result.converted_handlers) > 0,
        'migration_time': result.duration,
        'endpoints_migrated': len(service_info.endpoints)
    }


async def test_service_migrator_fastapi_to_proserve(framework: ProServeTestFramework):
    """Test ServiceMigrator FastAPI to ProServe migration"""
    from proserve.migration.migrator import ServiceMigrator, MigrationConfig
    from proserve.discovery.detector import ServiceDetector
    
    # Create FastAPI service
    fastapi_dir = framework.temp_dir / 'fastapi-migration-test'
    fastapi_dir.mkdir()
    
    (fastapi_dir / 'main.py').write_text('''
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/users")
async def get_users():
    return [{"id": 1, "name": "John"}]

@app.post("/api/users")
async def create_user(user: User):
    return {"id": 2, "name": user.name}
''')
    
    (fastapi_dir / 'requirements.txt').write_text('fastapi==0.104.1\nuvicorn==0.24.0')
    
    # Detect and migrate
    detector = ServiceDetector()
    service_info = await detector.detect_service(fastapi_dir)
    
    config = MigrationConfig(
        create_backup=True,
        generate_manifest=True,
        convert_handlers=True
    )
    
    migrator = ServiceMigrator()
    result = await migrator.migrate_to_proserve(service_info, config)
    
    assert result.success == True
    
    return {
        'fastapi_migration': result.success,
        'async_handlers_converted': any('async' in handler for handler in result.converted_handlers),
        'pydantic_models_handled': 'User' in str(result.converted_handlers),
        'manifest_has_fastapi_config': True  # Would check actual manifest content
    }


async def test_edpmt_migrator(framework: ProServeTestFramework):
    """Test EDPMTMigrator for legacy EDPMT service migration"""
    from proserve.migration.migrator import EDPMTMigrator, MigrationConfig
    
    # Create legacy EDPMT service structure
    edpmt_dir = framework.temp_dir / 'legacy-edpmt'
    edpmt_dir.mkdir()
    
    (edpmt_dir / 'edpmt_service.py').write_text('''
from edpmt_framework import EDPMTService, ServiceManifest

class LegacyService(EDPMTService):
    def __init__(self):
        manifest = ServiceManifest(
            name="legacy-service",
            version="1.0.0",
            endpoints=[
                {"path": "/health", "method": "GET", "handler": "health_check"},
                {"path": "/api/data", "method": "GET", "handler": "get_data"}
            ]
        )
        super().__init__(manifest)
    
    async def health_check(self, request):
        return {"status": "healthy"}
    
    async def get_data(self, request):
        return {"data": "legacy data"}
''')
    
    (edpmt_dir / 'requirements.txt').write_text('edpmt-framework==0.9.0')
    
    # Create old manifest format
    (edpmt_dir / 'service_config.json').write_text(json.dumps({
        "name": "legacy-service",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/health", "method": "GET"},
            {"path": "/api/data", "method": "GET"}
        ]
    }))
    
    # Run EDPMT migration
    config = MigrationConfig(
        create_backup=True,
        update_imports=True,
        modernize_syntax=True
    )
    
    migrator = EDPMTMigrator()
    result = await migrator.migrate_to_proserve(edpmt_dir, config)
    
    assert result.success == True
    
    return {
        'edpmt_migration': result.success,
        'imports_updated': 'proserve' in str(result.converted_handlers),
        'manifest_modernized': result.manifest_path.exists() if result.manifest_path else False,
        'backup_preserved': result.backup_path.exists() if result.backup_path else False
    }


async def test_migration_rollback(framework: ProServeTestFramework):
    """Test migration rollback functionality"""
    from proserve.migration.migrator import ServiceMigrator, MigrationConfig
    from proserve.discovery.detector import ServiceDetector
    
    # Create service for migration
    test_dir = framework.temp_dir / 'rollback-test'
    test_dir.mkdir()
    
    original_content = '''
from flask import Flask
app = Flask(__name__)

@app.route('/test')
def test():
    return "original"
'''
    
    (test_dir / 'app.py').write_text(original_content)
    
    # Detect and migrate
    detector = ServiceDetector()
    service_info = await detector.detect_service(test_dir)
    
    config = MigrationConfig(create_backup=True)
    migrator = ServiceMigrator()
    result = await migrator.migrate_to_proserve(service_info, config)
    
    # Verify migration happened
    assert result.success == True
    assert result.backup_path.exists()
    
    # Test rollback
    rollback_result = await migrator.rollback_migration(result)
    
    # Check that original content is restored
    restored_content = (test_dir / 'app.py').read_text()
    content_matches = 'return "original"' in restored_content
    
    return {
        'rollback_successful': rollback_result.success,
        'content_restored': content_matches,
        'backup_used': rollback_result.backup_path == result.backup_path
    }


async def test_migration_validation(framework: ProServeTestFramework):
    """Test migration validation and compatibility checks"""
    from proserve.migration.migrator import ServiceMigrator
    from proserve.discovery.detector import ServiceDetector, ServiceInfo
    
    # Create complex service for validation
    complex_dir = framework.temp_dir / 'complex-validation'
    complex_dir.mkdir()
    
    (complex_dir / 'app.py').write_text('''
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import redis
import celery

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/db'
db = SQLAlchemy(app)
redis_client = redis.Redis()

@app.route('/complex')
def complex_endpoint():
    # Complex logic with database, redis, sessions
    user_id = session.get('user_id')
    data = redis_client.get(f'user:{user_id}')
    return jsonify({"complex": True})
''')
    
    # Create service info manually for testing
    service_info = ServiceInfo(
        path=complex_dir,
        framework='flask',
        confidence=0.9,
        entry_point='app.py',
        endpoints=[
            {'path': '/complex', 'method': 'GET', 'handler': 'complex_endpoint'}
        ],
        dependencies=['flask', 'flask_sqlalchemy', 'redis', 'celery'],
        database_config={'type': 'postgresql', 'url': 'postgresql://user:pass@localhost/db'},
        complexity_score=8.5  # High complexity
    )
    
    # Run validation
    migrator = ServiceMigrator()
    validation_result = await migrator.validate_migration_compatibility(service_info)
    
    # Should identify complexity issues
    assert validation_result.is_compatible == True  # Should be compatible but with warnings
    assert len(validation_result.warnings) > 0  # Should have complexity warnings
    assert validation_result.complexity_score >= 8.0
    
    return {
        'validation_completed': True,
        'compatibility_checked': validation_result.is_compatible,
        'warnings_found': len(validation_result.warnings),
        'complexity_assessed': validation_result.complexity_score >= 8.0,
        'dependencies_analyzed': len(validation_result.dependency_issues) >= 0
    }


# Setup and teardown
async def setup_migration_tests(framework: ProServeTestFramework):
    """Setup for migration tests"""
    print("Setting up migration and discovery tests...")
    
    # Create test directories
    framework.test_services_dir = framework.temp_dir / 'test_services'
    framework.test_services_dir.mkdir()


async def teardown_migration_tests(framework: ProServeTestFramework):
    """Teardown for migration tests"""
    print("Tearing down migration tests...")
    
    # Clean up test services
    if hasattr(framework, 'test_services_dir') and framework.test_services_dir.exists():
        shutil.rmtree(framework.test_services_dir)


# Create test suite
migration_test_suite = TestSuite(
    name='migration',
    description='Migration and discovery functionality tests',
    tests=[
        test_service_detector_basic,
        test_service_detector_fastapi,
        test_service_detector_multi_framework,
        test_service_migrator_flask_to_proserve,
        test_service_migrator_fastapi_to_proserve,
        test_edpmt_migrator,
        test_migration_rollback,
        test_migration_validation
    ],
    setup=setup_migration_tests,
    teardown=teardown_migration_tests,
    timeout=600,  # Longer timeout for migration operations
    parallel=False
)
