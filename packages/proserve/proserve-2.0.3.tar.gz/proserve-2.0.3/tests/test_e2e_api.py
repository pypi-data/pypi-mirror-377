"""
ProServe E2E API Tests
Comprehensive API endpoint testing including REST, JSON, file uploads, and error handling
"""

import pytest
import json
import requests
import tempfile
from pathlib import Path
from .test_framework import ProServeTestFramework, assert_http_response


@pytest.mark.asyncio
async def test_rest_crud_operations(framework: ProServeTestFramework):
    """Test complete REST CRUD operations with JSON data"""
    manifest_path = framework.create_test_manifest(
        'test-rest-crud',
        endpoints=[
            {'path': '/api/items', 'method': 'get', 'handler': 'items_handler.handle'},
            {'path': '/api/items', 'method': 'post', 'handler': 'items_handler.handle'},
            {'path': '/api/items/{item_id}', 'method': 'get', 'handler': 'items_handler.handle'},
            {'path': '/api/items/{item_id}', 'method': 'put', 'handler': 'items_handler.handle'},
            {'path': '/api/items/{item_id}', 'method': 'delete', 'handler': 'items_handler.handle'},
        ]
    )
    
    # Create in-memory storage for testing
    storage_handler = '''
items_store = {}
next_id = 1

async def handle(request):
    global next_id
    method = request.method
    path = str(request.url.path)
    
    if method == 'GET' and path == '/api/items':
        return {"items": list(items_store.values()), "count": len(items_store)}, 200
    
    elif method == 'POST' and path == '/api/items':
        try:
            data = await request.json()
            item_id = str(next_id)
            next_id += 1
            item = {"id": item_id, "name": data.get("name"), "description": data.get("description")}
            items_store[item_id] = item
            return {"item": item, "status": "created"}, 201
        except:
            return {"error": "Invalid JSON"}, 400
    
    elif method == 'GET' and '/api/items/' in path:
        item_id = request.match_info.get('item_id')
        if item_id in items_store:
            return {"item": items_store[item_id]}, 200
        return {"error": "Item not found"}, 404
    
    elif method == 'PUT' and '/api/items/' in path:
        item_id = request.match_info.get('item_id')
        if item_id in items_store:
            try:
                data = await request.json()
                items_store[item_id].update(data)
                return {"item": items_store[item_id], "status": "updated"}, 200
            except:
                return {"error": "Invalid JSON"}, 400
        return {"error": "Item not found"}, 404
    
    elif method == 'DELETE' and '/api/items/' in path:
        item_id = request.match_info.get('item_id')
        if item_id in items_store:
            del items_store[item_id]
            return {"status": "deleted", "item_id": item_id}, 200
        return {"error": "Item not found"}, 404
    
    return {"error": "Method not allowed"}, 405
'''
    
    # Create single handler for all operations
    framework.create_test_handler('items_handler.py', storage_handler)
    
    service = await framework.start_test_service(manifest_path, 'crud_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test CREATE (POST)
    new_item = {"name": "Test Item", "description": "Test Description"}
    create_response = requests.post(f"{base_url}/api/items", json=new_item)
    assert create_response.status_code == 200
    created_item = create_response.json()["item"]
    item_id = created_item["id"]
    
    # Test READ LIST (GET all)
    list_response = await assert_http_response(f"{base_url}/api/items")
    assert len(list_response["items"]) == 1
    assert list_response["count"] == 1
    
    # Test READ ONE (GET by id)
    get_response = await assert_http_response(f"{base_url}/api/items/{item_id}")
    assert get_response["item"]["id"] == item_id
    assert get_response["item"]["name"] == "Test Item"
    
    # Test UPDATE (PUT)
    update_data = {"name": "Updated Item", "description": "Updated Description"}
    update_response = requests.put(f"{base_url}/api/items/{item_id}", json=update_data)
    assert update_response.status_code == 200
    assert update_response.json()["item"]["name"] == "Updated Item"
    
    # Test DELETE
    delete_response = requests.delete(f"{base_url}/api/items/{item_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "deleted"
    
    # Test 404 after deletion
    not_found_response = requests.get(f"{base_url}/api/items/{item_id}")
    assert not_found_response.status_code == 404
    
    return {
        "crud_operations": "success",
        "created_item": created_item,
        "update_status": update_response.json()["status"],
        "delete_status": delete_response.json()["status"]
    }


@pytest.mark.asyncio
async def test_file_upload_download(framework: ProServeTestFramework):
    """Test file upload and download functionality"""
    manifest_path = framework.create_test_manifest(
        'test-file-upload',
        endpoints=[
            {'path': '/api/upload', 'method': 'post', 'handler': 'file_handler.handle'},
            {'path': '/api/files/{filename}', 'method': 'get', 'handler': 'file_handler.handle'},
            {'path': '/api/files', 'method': 'get', 'handler': 'file_handler.handle'},
        ]
    )
    
    file_handler = '''
import os
from pathlib import Path
from aiohttp import web
import aiofiles

upload_dir = Path("/tmp/proserve_test_uploads")
upload_dir.mkdir(exist_ok=True)

async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    if method == 'POST' and path == '/api/upload':
        reader = await request.multipart()
        field = await reader.next()
        
        if field.name == 'file':
            filename = field.filename or 'upload.txt'
            file_path = upload_dir / filename
            
            with open(file_path, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)
            
            return {"filename": filename, "size": file_path.stat().st_size, "status": "uploaded"}
        
        return {"error": "No file provided"}, 400
    
    elif method == 'GET' and path == '/api/files':
        files = []
        for file_path in upload_dir.glob('*'):
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size
                })
        return {"files": files, "count": len(files)}
    
    elif method == 'GET' and '/api/files/' in path:
        filename = request.match_info.get('filename')
        file_path = upload_dir / filename
        
        if file_path.exists():
            return web.FileResponse(file_path)
        
        return {"error": "File not found"}, 404
    
    return {"error": "Method not allowed"}, 405
'''
    
    framework.create_test_handler('file_handler.py', file_handler)
    
    service = await framework.start_test_service(manifest_path, 'file_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Create test file
    test_content = b"This is a test file content for ProServe E2E testing"
    
    # Test file upload
    files = {'file': ('test.txt', test_content, 'text/plain')}
    upload_response = requests.post(f"{base_url}/api/upload", files=files)
    assert upload_response.status_code == 200
    upload_result = upload_response.json()
    assert upload_result["filename"] == "test.txt"
    assert upload_result["status"] == "uploaded"
    
    # Test files list
    list_response = await assert_http_response(f"{base_url}/api/files")
    assert len(list_response["files"]) >= 1
    assert any(f["filename"] == "test.txt" for f in list_response["files"])
    
    # Test file download
    download_response = requests.get(f"{base_url}/api/files/test.txt")
    assert download_response.status_code == 200
    assert download_response.content == test_content
    
    return {
        "upload_status": upload_result["status"],
        "file_count": len(list_response["files"]),
        "download_success": download_response.content == test_content
    }


@pytest.mark.asyncio
async def test_api_error_handling(framework: ProServeTestFramework):
    """Test API error handling and validation"""
    manifest_path = framework.create_test_manifest(
        'test-api-errors',
        endpoints=[
            {'path': '/api/validate', 'method': 'post', 'handler': 'error_handler.handle'},
            {'path': '/api/protected', 'method': 'get', 'handler': 'error_handler.handle'},
            {'path': '/api/timeout', 'method': 'get', 'handler': 'error_handler.handle'},
        ]
    )
    
    error_handler = '''
import asyncio
from aiohttp import web

async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    if method == 'POST' and path == '/api/validate':
        try:
            data = await request.json()
            
            # Validation rules
            errors = []
            if not data.get('name'):
                errors.append("Name is required")
            if not data.get('email'):
                errors.append("Email is required")
            elif '@' not in data.get('email', ''):
                errors.append("Invalid email format")
            if data.get('age') and (not isinstance(data['age'], int) or data['age'] < 0):
                errors.append("Age must be a positive integer")
            
            if errors:
                return {"errors": errors, "valid": False}, 400
            
            return {"message": "Validation passed", "valid": True, "data": data}
        
        except Exception as e:
            return {"error": "Invalid JSON format", "details": str(e)}, 400
    
    elif method == 'GET' and path == '/api/protected':
        auth_header = request.headers.get('Authorization')
        if not auth_header or auth_header != 'Bearer secret-token':
            return {"error": "Unauthorized", "message": "Valid token required"}, 401
        
        return {"message": "Access granted", "user": "test-user"}
    
    elif method == 'GET' and path == '/api/timeout':
        # Simulate timeout scenario
        await asyncio.sleep(0.1)  # Short delay for testing
        return {"message": "Request completed", "delayed": True}
    
    return {"error": "Not found"}, 404
'''
    
    framework.create_test_handler('error_handler.py', error_handler)
    
    service = await framework.start_test_service(manifest_path, 'error_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test validation errors
    invalid_data = {"name": "", "email": "invalid-email", "age": -5}
    validation_response = requests.post(f"{base_url}/api/validate", json=invalid_data)
    assert validation_response.status_code == 400
    validation_result = validation_response.json()
    assert not validation_result["valid"]
    assert len(validation_result["errors"]) >= 2
    
    # Test valid data
    valid_data = {"name": "John Doe", "email": "john@example.com", "age": 30}
    valid_response = requests.post(f"{base_url}/api/validate", json=valid_data)
    assert valid_response.status_code == 200
    assert valid_response.json()["valid"]
    
    # Test unauthorized access
    unauth_response = requests.get(f"{base_url}/api/protected")
    assert unauth_response.status_code == 401
    
    # Test authorized access
    headers = {"Authorization": "Bearer secret-token"}
    auth_response = requests.get(f"{base_url}/api/protected", headers=headers)
    assert auth_response.status_code == 200
    assert auth_response.json()["user"] == "test-user"
    
    # Test timeout endpoint
    timeout_response = await assert_http_response(f"{base_url}/api/timeout")
    assert timeout_response["delayed"]
    
    # Test 404 for non-existent endpoint
    not_found_response = requests.get(f"{base_url}/api/nonexistent")
    assert not_found_response.status_code == 404
    
    return {
        "validation_errors_count": len(validation_result["errors"]),
        "auth_test_passed": auth_response.status_code == 200,
        "timeout_handled": timeout_response["delayed"],
        "not_found_handled": not_found_response.status_code == 404
    }


@pytest.mark.asyncio
async def test_api_middleware_and_cors(framework: ProServeTestFramework):
    """Test API middleware, CORS, and request processing pipeline"""
    manifest_path = framework.create_test_manifest(
        'test-api-middleware',
        enable_cors=True,
        cors_origins=['*'],
        endpoints=[
            {'path': '/api/middleware-test', 'method': 'get', 'handler': 'middleware_handler.handle'},
            {'path': '/api/headers', 'method': 'get', 'handler': 'middleware_handler.handle'},
        ]
    )
    
    middleware_handler = '''
async def handle(request):
    method = request.method
    path = str(request.url.path)
    
    if path == '/api/middleware-test':
        # Test request processing
        user_agent = request.headers.get('User-Agent', 'unknown')
        content_type = request.headers.get('Content-Type', 'none')
        
        return {
            "method": method,
            "path": path,
            "user_agent": user_agent,
            "content_type": content_type,
            "headers_count": len(request.headers),
            "query_params": dict(request.query),
            "timestamp": str(request.headers.get('X-Request-Time', 'none'))
        }
    
    elif path == '/api/headers':
        # Return all headers for inspection
        return {
            "headers": dict(request.headers),
            "method": method,
            "host": request.host,
            "scheme": request.scheme,
            "query_string": request.query_string
        }
    
    return {"error": "Not found"}, 404
'''
    
    framework.create_test_handler('middleware_handler.py', middleware_handler)
    
    service = await framework.start_test_service(manifest_path, 'middleware_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Test middleware processing
    custom_headers = {
        'User-Agent': 'ProServe-E2E-Test/1.0',
        'X-Request-Time': '2025-01-17T12:00:00Z',
        'Content-Type': 'application/json'
    }
    
    middleware_response = requests.get(
        f"{base_url}/api/middleware-test?param1=value1&param2=value2", 
        headers=custom_headers
    )
    assert middleware_response.status_code == 200
    middleware_result = middleware_response.json()
    
    assert middleware_result["method"] == "GET"
    assert middleware_result["user_agent"] == "ProServe-E2E-Test/1.0"
    assert middleware_result["query_params"]["param1"] == "value1"
    
    # Test CORS headers
    cors_response = requests.options(f"{base_url}/api/middleware-test")
    assert 'Access-Control-Allow-Origin' in cors_response.headers
    
    # Test headers inspection
    headers_response = await assert_http_response(f"{base_url}/api/headers")
    assert "headers" in headers_response
    assert headers_response["method"] == "GET"
    
    return {
        "middleware_processed": middleware_result["headers_count"] > 0,
        "cors_enabled": 'Access-Control-Allow-Origin' in cors_response.headers,
        "query_params_parsed": len(middleware_result["query_params"]) == 2,
        "custom_headers_received": middleware_result["user_agent"] == "ProServe-E2E-Test/1.0"
    }
