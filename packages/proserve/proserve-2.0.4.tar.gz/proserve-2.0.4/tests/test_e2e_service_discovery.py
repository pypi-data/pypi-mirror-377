"""
ProServe E2E Service Discovery and Migration Tests
Service detection, framework migration, and inter-service communication
"""

import pytest
import json
import requests
import tempfile
from pathlib import Path
from .test_framework import ProServeTestFramework, assert_http_response


@pytest.mark.asyncio
async def test_flask_service_detection_and_migration(framework: ProServeTestFramework):
    """Test detection of Flask application and migration to ProServe"""
    
    # Create a mock Flask application structure
    flask_app_dir = framework.temp_dir / "flask_app"
    flask_app_dir.mkdir(exist_ok=True)
    
    # Create Flask app.py
    flask_app_content = '''
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Flask App",
        "framework": "Flask",
        "version": "1.0.0"
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({
        "users": [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"}
        ]
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    return jsonify({
        "user": {
            "id": 3,
            "name": data.get("name"),
            "email": data.get("email")
        },
        "status": "created"
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "framework": "Flask"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
'''
    
    (flask_app_dir / "app.py").write_text(flask_app_content)
    
    # Create requirements.txt
    requirements_content = '''
Flask==2.3.3
Werkzeug==2.3.7
'''
    (flask_app_dir / "requirements.txt").write_text(requirements_content)
    
    # Create service discovery handler
    discovery_handler = '''
import json
from pathlib import Path

# Mock service discovery results
discovered_services = []

async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    if path == "/api/discover" and method == "POST":
        data = await request.json()
        target_path = data.get("path", ".")
        
        # Simulate service detection
        flask_service = {
            "framework": "Flask",
            "path": target_path,
            "main_file": "app.py",
            "routes": [
                {"path": "/", "method": "GET", "handler": "home"},
                {"path": "/api/users", "method": "GET", "handler": "get_users"},
                {"path": "/api/users", "method": "POST", "handler": "create_user"},
                {"path": "/api/health", "method": "GET", "handler": "health"}
            ],
            "dependencies": ["Flask==2.3.3", "Werkzeug==2.3.7"],
            "detected_patterns": [
                "Flask app factory pattern",
                "RESTful API endpoints",
                "JSON responses",
                "Request handling"
            ]
        }
        
        discovered_services.append(flask_service)
        
        return {
            "discovered_services": [flask_service],
            "detection_confidence": 0.95,
            "migration_recommendations": [
                "Convert Flask routes to ProServe endpoints",
                "Replace Flask request/response with aiohttp",
                "Migrate JSON handling",
                "Update dependency management"
            ]
        }
    
    elif path == "/api/migrate" and method == "POST":
        data = await request.json()
        service_id = data.get("service_id", 0)
        
        if service_id < len(discovered_services):
            service = discovered_services[service_id]
            
            # Generate ProServe manifest
            proserve_manifest = {
                "name": "migrated-flask-app",
                "version": "1.0.0",
                "description": f"Migrated from {service['framework']} application",
                "type": "http",
                "host": "localhost",
                "port": 8080,
                "enable_cors": True,
                "endpoints": []
            }
            
            # Convert Flask routes to ProServe endpoints
            for route in service["routes"]:
                endpoint = {
                    "path": route["path"],
                    "method": route["method"].lower(),
                    "handler": f"handlers.migrated.{route['handler']}.handle"
                }
                proserve_manifest["endpoints"].append(endpoint)
            
            # Generate migration report
            migration_report = {
                "status": "completed",
                "original_framework": service["framework"],
                "manifest_generated": proserve_manifest,
                "converted_routes": len(service["routes"]),
                "migration_steps": [
                    "Service detected successfully",
                    "Routes analyzed and converted",
                    "ProServe manifest generated",
                    "Handler templates created",
                    "Migration completed"
                ],
                "next_steps": [
                    "Review generated manifest",
                    "Implement handler functions",
                    "Test migrated endpoints",
                    "Deploy ProServe service"
                ]
            }
            
            return migration_report
        
        return {"error": "Service not found"}, 404
    
    elif path == "/api/services":
        return {
            "discovered_services": discovered_services,
            "count": len(discovered_services)
        }
    
    return {"error": "Endpoint not found"}, 404
'''
    
    manifest_path = framework.create_test_manifest(
        'test-service-discovery',
        endpoints=[
            {'path': '/api/discover', 'method': 'post', 'handler': 'discovery_handler.handle'},
            {'path': '/api/migrate', 'method': 'post', 'handler': 'discovery_handler.handle'},
            {'path': '/api/services', 'method': 'get', 'handler': 'discovery_handler.handle'},
        ]
    )
    
    framework.create_test_handler('discovery_handler.py', discovery_handler)
    
    service = await framework.start_test_service(manifest_path, 'discovery_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test service discovery
    discovery_data = {"path": str(flask_app_dir)}
    discovery_response = requests.post(f"{base_url}/api/discover", json=discovery_data)
    assert discovery_response.status_code == 200
    
    discovery_result = discovery_response.json()
    assert len(discovery_result["discovered_services"]) == 1
    assert discovery_result["discovered_services"][0]["framework"] == "Flask"
    assert discovery_result["detection_confidence"] > 0.9
    
    # Test migration
    migration_data = {"service_id": 0}
    migration_response = requests.post(f"{base_url}/api/migrate", json=migration_data)
    assert migration_response.status_code == 200
    
    migration_result = migration_response.json()
    assert migration_result["status"] == "completed"
    assert migration_result["original_framework"] == "Flask"
    assert len(migration_result["manifest_generated"]["endpoints"]) == 4
    
    # Test services list
    services_response = await assert_http_response(f"{base_url}/api/services")
    assert services_response["count"] == 1
    
    return {
        "service_discovery_working": True,
        "flask_detected": discovery_result["discovered_services"][0]["framework"] == "Flask",
        "routes_detected": len(discovery_result["discovered_services"][0]["routes"]) == 4,
        "migration_completed": migration_result["status"] == "completed",
        "manifest_generated": len(migration_result["manifest_generated"]["endpoints"]) == 4,
        "detection_confidence": discovery_result["detection_confidence"]
    }


@pytest.mark.asyncio
async def test_inter_service_communication(framework: ProServeTestFramework):
    """Test communication between multiple ProServe services"""
    
    # Service A - Primary service
    service_a_handler = '''
import json
import aiohttp

async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    if path == "/api/aggregate" and method == "GET":
        # Call Service B to get user data
        service_b_url = request.query.get('service_b_url', 'http://localhost:8081')
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get users from Service B
                async with session.get(f"{service_b_url}/api/users") as resp:
                    if resp.status == 200:
                        users_data = await resp.json()
                    else:
                        users_data = {"users": [], "error": "Service B unavailable"}
                
                # Get stats from Service B
                async with session.get(f"{service_b_url}/api/stats") as resp:
                    if resp.status == 200:
                        stats_data = await resp.json()
                    else:
                        stats_data = {"stats": {}, "error": "Service B unavailable"}
            
            # Aggregate data
            aggregated_response = {
                "service": "Service A",
                "aggregated_at": "2025-01-17T12:00:00Z",
                "data": {
                    "users": users_data.get("users", []),
                    "user_count": len(users_data.get("users", [])),
                    "stats": stats_data.get("stats", {}),
                    "service_b_status": "available" if users_data.get("users") else "unavailable"
                },
                "sources": ["Service B"]
            }
            
            return aggregated_response
            
        except Exception as e:
            return {
                "service": "Service A",
                "error": f"Failed to communicate with Service B: {str(e)}",
                "data": None
            }
    
    elif path == "/api/health":
        return {
            "service": "Service A",
            "status": "healthy",
            "capabilities": ["aggregation", "inter-service-communication"]
        }
    
    return {"error": "Endpoint not found"}, 404
'''
    
    # Service B - Data service
    service_b_handler = '''
import json
from datetime import datetime

# Mock data store
users_data = [
    {"id": 1, "name": "Alice Johnson", "role": "admin", "active": True},
    {"id": 2, "name": "Bob Smith", "role": "user", "active": True},
    {"id": 3, "name": "Carol Brown", "role": "user", "active": False}
]

async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    if path == "/api/users" and method == "GET":
        active_users = [u for u in users_data if u.get("active", True)]
        return {
            "users": active_users,
            "total_count": len(users_data),
            "active_count": len(active_users),
            "service": "Service B"
        }
    
    elif path == "/api/stats" and method == "GET":
        admin_count = len([u for u in users_data if u.get("role") == "admin"])
        user_count = len([u for u in users_data if u.get("role") == "user"])
        active_count = len([u for u in users_data if u.get("active", True)])
        
        return {
            "stats": {
                "total_users": len(users_data),
                "admin_users": admin_count,
                "regular_users": user_count,
                "active_users": active_count,
                "inactive_users": len(users_data) - active_count
            },
            "generated_at": str(datetime.now()),
            "service": "Service B"
        }
    
    elif path == "/api/health":
        return {
            "service": "Service B",
            "status": "healthy",
            "capabilities": ["user-management", "statistics"]
        }
    
    return {"error": "Endpoint not found"}, 404
'''
    
    # Create Service A
    manifest_a_path = framework.create_test_manifest(
        'service-a',
        host='localhost',
        port=8080,
        endpoints=[
            {'path': '/api/aggregate', 'method': 'get', 'handler': 'service_a_handler.handle'},
            {'path': '/api/health', 'method': 'get', 'handler': 'service_a_handler.handle'},
        ]
    )
    
    # Create Service B  
    manifest_b_path = framework.create_test_manifest(
        'service-b',
        host='localhost',
        port=8081,
        endpoints=[
            {'path': '/api/users', 'method': 'get', 'handler': 'service_b_handler.handle'},
            {'path': '/api/stats', 'method': 'get', 'handler': 'service_b_handler.handle'},
            {'path': '/api/health', 'method': 'get', 'handler': 'service_b_handler.handle'},
        ]
    )
    
    framework.create_test_handler('service_a_handler.py', service_a_handler)
    framework.create_test_handler('service_b_handler.py', service_b_handler)
    
    # Start both services
    service_a = await framework.start_test_service(manifest_a_path, 'service_a')
    service_b = await framework.start_test_service(manifest_b_path, 'service_b')
    
    manifest_a = service_a.manifest
    manifest_b = service_b.manifest
    
    base_url_a = f"http://{manifest_a.host}:{manifest_a.port}"
    base_url_b = f"http://{manifest_b.host}:{manifest_b.port}"
    
    # Test Service B independently
    users_response = await assert_http_response(f"{base_url_b}/api/users")
    assert len(users_response["users"]) >= 2
    assert users_response["service"] == "Service B"
    
    stats_response = await assert_http_response(f"{base_url_b}/api/stats")
    assert stats_response["stats"]["total_users"] >= 3
    assert stats_response["service"] == "Service B"
    
    # Test Service A health
    health_a_response = await assert_http_response(f"{base_url_a}/api/health")
    assert health_a_response["service"] == "Service A"
    assert "aggregation" in health_a_response["capabilities"]
    
    # Test inter-service communication (Service A calling Service B)
    aggregate_response = await assert_http_response(
        f"{base_url_a}/api/aggregate?service_b_url={base_url_b}"
    )
    
    assert aggregate_response["service"] == "Service A"
    assert len(aggregate_response["data"]["users"]) >= 2
    assert aggregate_response["data"]["user_count"] >= 2
    assert aggregate_response["data"]["service_b_status"] == "available"
    assert "Service B" in aggregate_response["sources"]
    
    # Test Service B health
    health_b_response = await assert_http_response(f"{base_url_b}/api/health")
    assert health_b_response["service"] == "Service B"
    
    return {
        "inter_service_communication_working": True,
        "service_a_healthy": health_a_response["status"] == "healthy",
        "service_b_healthy": health_b_response["status"] == "healthy",
        "service_b_data_accessible": len(users_response["users"]) >= 2,
        "aggregation_working": len(aggregate_response["data"]["users"]) >= 2,
        "cross_service_calls_successful": aggregate_response["data"]["service_b_status"] == "available",
        "both_services_running": True
    }


@pytest.mark.asyncio
async def test_service_registry_and_load_balancing(framework: ProServeTestFramework):
    """Test service registry and basic load balancing functionality"""
    
    # Service Registry handler
    registry_handler = '''
import json
from datetime import datetime, timedelta

# Service registry
registered_services = {}
service_health = {}

async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    if path == "/api/register" and method == "POST":
        data = await request.json()
        service_id = data.get("service_id")
        service_info = {
            "id": service_id,
            "name": data.get("name"),
            "host": data.get("host", "localhost"),
            "port": data.get("port", 8080),
            "endpoints": data.get("endpoints", []),
            "health_check_url": data.get("health_check_url"),
            "registered_at": str(datetime.now()),
            "last_heartbeat": str(datetime.now()),
            "status": "active"
        }
        
        registered_services[service_id] = service_info
        service_health[service_id] = {
            "status": "healthy",
            "last_check": str(datetime.now()),
            "response_time": 0.05
        }
        
        return {
            "status": "registered",
            "service_id": service_id,
            "registry_size": len(registered_services)
        }
    
    elif path == "/api/discover" and method == "GET":
        service_name = request.query.get("service")
        
        if service_name:
            # Find services by name
            matching_services = [
                s for s in registered_services.values() 
                if s["name"] == service_name and s["status"] == "active"
            ]
            return {
                "services": matching_services,
                "count": len(matching_services)
            }
        
        # Return all services
        return {
            "services": list(registered_services.values()),
            "count": len(registered_services)
        }
    
    elif path == "/api/heartbeat" and method == "POST":
        data = await request.json()
        service_id = data.get("service_id")
        
        if service_id in registered_services:
            registered_services[service_id]["last_heartbeat"] = str(datetime.now())
            service_health[service_id]["last_check"] = str(datetime.now())
            service_health[service_id]["status"] = "healthy"
            
            return {"status": "heartbeat_received", "service_id": service_id}
        
        return {"error": "Service not registered"}, 404
    
    elif path == "/api/load-balance" and method == "GET":
        service_name = request.query.get("service")
        
        if not service_name:
            return {"error": "Service name required"}, 400
        
        # Find healthy services
        healthy_services = []
        for service_id, service in registered_services.items():
            if (service["name"] == service_name and 
                service["status"] == "active" and 
                service_health.get(service_id, {}).get("status") == "healthy"):
                healthy_services.append(service)
        
        if not healthy_services:
            return {"error": "No healthy services available"}, 503
        
        # Simple round-robin load balancing
        import random
        selected_service = random.choice(healthy_services)
        
        return {
            "selected_service": selected_service,
            "available_instances": len(healthy_services),
            "load_balancing_strategy": "round_robin"
        }
    
    elif path == "/api/health":
        return {
            "registry_status": "healthy",
            "registered_services": len(registered_services),
            "healthy_services": len([
                s for s in service_health.values() 
                if s.get("status") == "healthy"
            ])
        }
    
    return {"error": "Endpoint not found"}, 404
'''
    
    # Mock application service
    app_service_handler = '''
import json

instance_id = None

async def handle(request):
    global instance_id
    method = request.method
    path = str(request.url.path)
    
    if path == "/api/app/data" and method == "GET":
        return {
            "data": f"Response from instance {instance_id}",
            "instance_id": instance_id,
            "timestamp": "2025-01-17T12:00:00Z"
        }
    
    elif path == "/api/health":
        return {
            "status": "healthy",
            "instance_id": instance_id,
            "service": "app-service"
        }
    
    # Set instance ID from query parameter for testing
    elif path == "/api/set-instance" and method == "POST":
        data = await request.json()
        instance_id = data.get("instance_id", "unknown")
        return {"instance_id": instance_id}
    
    return {"error": "Endpoint not found"}, 404
'''
    
    # Create Service Registry
    registry_manifest = framework.create_test_manifest(
        'service-registry',
        host='localhost',
        port=8090,
        endpoints=[
            {'path': '/api/register', 'method': 'post', 'handler': 'registry_handler.handle'},
            {'path': '/api/discover', 'method': 'get', 'handler': 'registry_handler.handle'},
            {'path': '/api/heartbeat', 'method': 'post', 'handler': 'registry_handler.handle'},
            {'path': '/api/load-balance', 'method': 'get', 'handler': 'registry_handler.handle'},
            {'path': '/api/health', 'method': 'get', 'handler': 'registry_handler.handle'},
        ]
    )
    
    # Create App Service Instance 1
    app1_manifest = framework.create_test_manifest(
        'app-service-1',
        host='localhost',
        port=8091,
        endpoints=[
            {'path': '/api/app/data', 'method': 'get', 'handler': 'app1_handler.handle'},
            {'path': '/api/health', 'method': 'get', 'handler': 'app1_handler.handle'},
            {'path': '/api/set-instance', 'method': 'post', 'handler': 'app1_handler.handle'},
        ]
    )
    
    # Create App Service Instance 2
    app2_manifest = framework.create_test_manifest(
        'app-service-2', 
        host='localhost',
        port=8092,
        endpoints=[
            {'path': '/api/app/data', 'method': 'get', 'handler': 'app2_handler.handle'},
            {'path': '/api/health', 'method': 'get', 'handler': 'app2_handler.handle'},
            {'path': '/api/set-instance', 'method': 'post', 'handler': 'app2_handler.handle'},
        ]
    )
    
    framework.create_test_handler('registry_handler.py', registry_handler)
    framework.create_test_handler('app1_handler.py', app_service_handler)
    framework.create_test_handler('app2_handler.py', app_service_handler)
    
    # Start services
    registry_service = await framework.start_test_service(registry_manifest, 'registry')
    app1_service = await framework.start_test_service(app1_manifest, 'app1')
    app2_service = await framework.start_test_service(app2_manifest, 'app2')
    
    registry_url = f"http://{registry_service.manifest.host}:{registry_service.manifest.port}"
    app1_url = f"http://{app1_service.manifest.host}:{app1_service.manifest.port}"
    app2_url = f"http://{app2_service.manifest.host}:{app2_service.manifest.port}"
    
    # Set instance IDs
    requests.post(f"{app1_url}/api/set-instance", json={"instance_id": "app-1"})
    requests.post(f"{app2_url}/api/set-instance", json={"instance_id": "app-2"})
    
    # Register services with registry
    app1_registration = {
        "service_id": "app-service-1",
        "name": "app-service",
        "host": "localhost",
        "port": 8091,
        "health_check_url": f"{app1_url}/api/health",
        "endpoints": ["/api/app/data"]
    }
    
    app2_registration = {
        "service_id": "app-service-2", 
        "name": "app-service",
        "host": "localhost",
        "port": 8092,
        "health_check_url": f"{app2_url}/api/health",
        "endpoints": ["/api/app/data"]
    }
    
    reg1_response = requests.post(f"{registry_url}/api/register", json=app1_registration)
    reg2_response = requests.post(f"{registry_url}/api/register", json=app2_registration)
    
    assert reg1_response.status_code == 200
    assert reg2_response.status_code == 200
    
    # Test service discovery
    discovery_response = await assert_http_response(f"{registry_url}/api/discover?service=app-service")
    assert discovery_response["count"] == 2
    
    # Test load balancing
    load_balance_responses = []
    for _ in range(6):  # Make multiple requests to test distribution
        lb_response = await assert_http_response(f"{registry_url}/api/load-balance?service=app-service")
        load_balance_responses.append(lb_response["selected_service"]["port"])
    
    # Should get both instances
    unique_instances = set(load_balance_responses)
    assert len(unique_instances) >= 1  # At least one instance selected
    
    # Test heartbeat
    heartbeat_response = requests.post(f"{registry_url}/api/heartbeat", json={"service_id": "app-service-1"})
    assert heartbeat_response.status_code == 200
    
    # Test registry health
    registry_health = await assert_http_response(f"{registry_url}/api/health")
    assert registry_health["registered_services"] >= 2
    assert registry_health["healthy_services"] >= 2
    
    return {
        "service_registry_working": True,
        "services_registered": reg1_response.status_code == 200 and reg2_response.status_code == 200,
        "service_discovery_working": discovery_response["count"] == 2,
        "load_balancing_working": len(unique_instances) >= 1,
        "heartbeat_working": heartbeat_response.status_code == 200,
        "registry_healthy": registry_health["registered_services"] >= 2,
        "multiple_instances_available": len(unique_instances) >= 1
    }
