"""
ProServe E2E Performance and Monitoring Tests
Load testing, metrics collection, and performance monitoring
"""

import pytest
import asyncio
import time
import concurrent.futures
import requests
from .test_framework import ProServeTestFramework, assert_http_response


@pytest.mark.asyncio
async def test_concurrent_load_handling(framework: ProServeTestFramework):
    """Test service under concurrent load"""
    
    load_handler = '''
import asyncio
import time
from datetime import datetime

request_count = 0
processing_times = []

async def handle(request):
    global request_count, processing_times
    start_time = time.time()
    
    path = str(request.url.path)
    
    if path == "/api/load-test":
        request_count += 1
        
        # Simulate processing
        await asyncio.sleep(0.01)
        
        processing_time = time.time() - start_time
        processing_times.append(processing_time)
        
        return {
            "request_id": request_count,
            "processing_time": processing_time,
            "timestamp": str(datetime.now())
        }
    
    elif path == "/api/metrics":
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
        return {
            "total_requests": request_count,
            "avg_processing_time": avg_time,
            "min_time": min(processing_times) if processing_times else 0,
            "max_time": max(processing_times) if processing_times else 0
        }
    
    return {"error": "Not found"}, 404
'''
    
    manifest_path = framework.create_test_manifest(
        'load-test-service',
        endpoints=[
            {'path': '/api/load-test', 'method': 'get', 'handler': 'load_handler.handle'},
            {'path': '/api/metrics', 'method': 'get', 'handler': 'load_handler.handle'},
        ]
    )
    
    framework.create_test_handler('load_handler.py', load_handler)
    
    service = await framework.start_test_service(manifest_path, 'load_test')
    base_url = f"http://{service.manifest.host}:{service.manifest.port}"
    
    # Concurrent load test
    def make_request():
        return requests.get(f"{base_url}/api/load-test")
    
    # Execute 20 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    successful_requests = [r for r in results if r.status_code == 200]
    
    # Get metrics
    metrics_response = await assert_http_response(f"{base_url}/api/metrics")
    
    return {
        "concurrent_load_handled": len(successful_requests) >= 15,
        "total_requests_processed": metrics_response["total_requests"],
        "avg_processing_time": metrics_response["avg_processing_time"],
        "all_requests_successful": len(successful_requests) == 20
    }


@pytest.mark.asyncio
async def test_memory_and_resource_monitoring(framework: ProServeTestFramework):
    """Test memory usage and resource monitoring"""
    
    monitoring_handler = '''
import psutil
import os
from datetime import datetime

async def handle(request):
    path = str(request.url.path)
    
    if path == "/api/system-stats":
        process = psutil.Process(os.getpid())
        
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "threads": process.num_threads(),
            "connections": len(process.connections()),
            "timestamp": str(datetime.now())
        }
    
    elif path == "/api/health-detailed":
        return {
            "status": "healthy",
            "uptime_seconds": time.time() - process_start_time,
            "system_load": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        }
    
    return {"error": "Not found"}, 404

process_start_time = __import__('time').time()
'''
    
    manifest_path = framework.create_test_manifest(
        'monitoring-service',
        endpoints=[
            {'path': '/api/system-stats', 'method': 'get', 'handler': 'monitor_handler.handle'},
            {'path': '/api/health-detailed', 'method': 'get', 'handler': 'monitor_handler.handle'},
        ]
    )
    
    framework.create_test_handler('monitor_handler.py', monitoring_handler)
    
    service = await framework.start_test_service(manifest_path, 'monitor_test')
    base_url = f"http://{service.manifest.host}:{service.manifest.port}"
    
    # Test system stats
    stats_response = await assert_http_response(f"{base_url}/api/system-stats")
    
    # Test health check
    health_response = await assert_http_response(f"{base_url}/api/health-detailed")
    
    return {
        "monitoring_working": True,
        "memory_tracked": "memory_mb" in stats_response,
        "cpu_tracked": "cpu_percent" in stats_response,
        "health_monitoring": health_response["status"] == "healthy",
        "uptime_tracked": "uptime_seconds" in health_response
    }
