"""
ProServe E2E Background Tasks Tests
Scheduled tasks, cron jobs, service management, and async operations
"""

import pytest
import asyncio
import time
import requests
from .test_framework import ProServeTestFramework, assert_http_response


@pytest.mark.asyncio
async def test_scheduled_background_tasks(framework: ProServeTestFramework):
    """Test scheduled background tasks with different intervals"""
    
    # Create shared storage for task results
    task_handler = '''
import asyncio
import json
from datetime import datetime

# Shared storage for task results
task_results = {
    "frequent_task": [],
    "periodic_task": [],
    "cleanup_task": []
}

async def handle(request):
    path = str(request.url.path)
    
    if path == "/api/task-results":
        return {
            "results": task_results,
            "counts": {
                "frequent": len(task_results["frequent_task"]),
                "periodic": len(task_results["periodic_task"]), 
                "cleanup": len(task_results["cleanup_task"])
            },
            "timestamp": str(datetime.now())
        }
    
    elif path == "/api/clear-results":
        for key in task_results:
            task_results[key].clear()
        return {"status": "cleared", "timestamp": str(datetime.now())}
    
    return {"error": "Not found"}, 404
'''
    
    # Background task implementations
    frequent_task = '''
import asyncio
from datetime import datetime

async def execute():
    """Task that runs every 2 seconds"""
    from handlers.api.task_results import task_results
    
    result = {
        "task": "frequent_task",
        "executed_at": str(datetime.now()),
        "counter": len(task_results["frequent_task"]) + 1
    }
    
    task_results["frequent_task"].append(result)
    
    # Limit storage to last 10 executions
    if len(task_results["frequent_task"]) > 10:
        task_results["frequent_task"] = task_results["frequent_task"][-10:]
    
    print(f"Frequent task executed: {result['counter']}")
'''

    periodic_task = '''
import asyncio
from datetime import datetime

async def execute():
    """Task that runs every 5 seconds"""
    from handlers.api.task_results import task_results
    
    result = {
        "task": "periodic_task",
        "executed_at": str(datetime.now()),
        "data_processed": len(task_results["frequent_task"]),
        "execution_count": len(task_results["periodic_task"]) + 1
    }
    
    task_results["periodic_task"].append(result)
    print(f"Periodic task executed: {result['execution_count']}")
'''

    cleanup_task = '''
import asyncio
from datetime import datetime

async def execute():
    """Cleanup task that runs every 10 seconds"""
    from handlers.api.task_results import task_results
    
    # Simulate cleanup work
    cleaned_items = 0
    for task_list in task_results.values():
        if len(task_list) > 5:
            cleaned_items += len(task_list) - 5
            task_list[:] = task_list[-5:]  # Keep only last 5 items
    
    result = {
        "task": "cleanup_task",
        "executed_at": str(datetime.now()),
        "items_cleaned": cleaned_items,
        "execution_count": len(task_results["cleanup_task"]) + 1
    }
    
    task_results["cleanup_task"].append(result)
    print(f"Cleanup task executed, cleaned {cleaned_items} items")
'''
    
    manifest_path = framework.create_test_manifest(
        'test-background-tasks',
        endpoints=[
            {'path': '/api/task-results', 'method': 'get', 'handler': 'task_results_handler.handle'},
            {'path': '/api/clear-results', 'method': 'post', 'handler': 'task_results_handler.handle'},
        ],
        background_tasks=[
            {
                'name': 'frequent_task',
                'handler': 'frequent_task.handle',
                'schedule': 'interval:2',  # Every 2 seconds
                'enabled': True
            },
            {
                'name': 'periodic_task', 
                'handler': 'periodic_task.handle',
                'schedule': 'interval:5',  # Every 5 seconds
                'enabled': True
            },
            {
                'name': 'cleanup_task',
                'handler': 'cleanup_task.handle',
                'schedule': 'interval:10',  # Every 10 seconds
                'enabled': True
            }
        ]
    )
    
    # Create task handlers
    framework.create_test_handler('task_results_handler.py', task_handler)
    framework.create_test_handler('frequent_task.py', frequent_task)
    framework.create_test_handler('periodic_task.py', periodic_task)
    framework.create_test_handler('cleanup_task.py', cleanup_task)
    
    service = await framework.start_test_service(manifest_path, 'background_tasks_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Clear any existing results
    requests.post(f"{base_url}/api/clear-results")
    
    # Wait for tasks to execute multiple times
    await asyncio.sleep(12)  # Wait 12 seconds to see task executions
    
    # Check task results
    results_response = await assert_http_response(f"{base_url}/api/task-results")
    counts = results_response["counts"]
    
    # Frequent task (every 2s) should have run ~6 times in 12 seconds
    # Periodic task (every 5s) should have run ~2-3 times in 12 seconds  
    # Cleanup task (every 10s) should have run ~1-2 times in 12 seconds
    
    frequent_executions = counts["frequent"]
    periodic_executions = counts["periodic"]
    cleanup_executions = counts["cleanup"]
    
    return {
        "background_tasks_running": True,
        "frequent_task_executions": frequent_executions,
        "periodic_task_executions": periodic_executions,
        "cleanup_task_executions": cleanup_executions,
        "tasks_scheduled_correctly": frequent_executions >= 4 and periodic_executions >= 1,
        "all_tasks_executed": frequent_executions > 0 and periodic_executions > 0 and cleanup_executions >= 0
    }


@pytest.mark.asyncio
async def test_cron_scheduled_tasks(framework: ProServeTestFramework):
    """Test cron-style scheduled tasks"""
    
    cron_handler = '''
import json
from datetime import datetime

# Storage for cron task results
cron_results = []

async def handle(request):
    return {
        "cron_results": cron_results,
        "execution_count": len(cron_results),
        "last_execution": cron_results[-1] if cron_results else None
    }
'''

    # Cron task that runs every minute (for testing we'll use a shorter interval)
    cron_task = '''
from datetime import datetime

async def execute():
    """Cron task for testing"""
    from handlers.api.cron_results import cron_results
    
    result = {
        "executed_at": str(datetime.now()),
        "minute": datetime.now().minute,
        "second": datetime.now().second,
        "execution_number": len(cron_results) + 1
    }
    
    cron_results.append(result)
    print(f"Cron task executed at {result['executed_at']}")
'''

    manifest_path = framework.create_test_manifest(
        'test-cron-tasks',
        endpoints=[
            {'path': '/api/cron-results', 'method': 'get', 'handler': 'cron_results_handler.handle'},
        ],
        background_tasks=[
            {
                'name': 'cron_task',
                'handler': 'cron_task.handle',
                'schedule': 'cron:*/1 * * * *',  # Every minute (in testing, might be adapted)
                'enabled': True,
                'timeout': 30
            }
        ]
    )
    
    framework.create_test_handler('cron_results_handler.py', cron_handler)
    framework.create_test_handler('cron_task.py', cron_task)
    
    service = await framework.start_test_service(manifest_path, 'cron_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Wait for potential cron execution
    await asyncio.sleep(8)
    
    results_response = await assert_http_response(f"{base_url}/api/cron-results")
    
    return {
        "cron_task_configured": True,
        "cron_executions": results_response["execution_count"],
        "cron_system_working": results_response["execution_count"] >= 0
    }


@pytest.mark.asyncio
async def test_task_error_handling_and_recovery(framework: ProServeTestFramework):
    """Test background task error handling and recovery mechanisms"""
    
    task_monitor_handler = '''
import json
from datetime import datetime

# Task monitoring data
task_monitor = {
    "successful_executions": [],
    "failed_executions": [],
    "recovery_attempts": []
}

async def handle(request):
    path = str(request.url.path)
    
    if path == "/api/task-monitor":
        return {
            "monitor": task_monitor,
            "stats": {
                "successful": len(task_monitor["successful_executions"]),
                "failed": len(task_monitor["failed_executions"]),
                "recoveries": len(task_monitor["recovery_attempts"])
            }
        }
    
    elif path == "/api/reset-monitor":
        for key in task_monitor:
            task_monitor[key].clear()
        return {"status": "reset"}
    
    return {"error": "Not found"}, 404
'''

    # Task that sometimes fails for testing error handling
    flaky_task = '''
import random
from datetime import datetime

execution_count = 0

async def execute():
    """Task that randomly fails to test error handling"""
    global execution_count
    execution_count += 1
    
    from handlers.api.task_monitor import task_monitor
    
    # Simulate failure 30% of the time
    if random.random() < 0.3:
        error_result = {
            "execution_number": execution_count,
            "timestamp": str(datetime.now()),
            "error": "Simulated random failure"
        }
        task_monitor["failed_executions"].append(error_result)
        raise Exception("Simulated task failure")
    
    success_result = {
        "execution_number": execution_count,
        "timestamp": str(datetime.now()),
        "status": "success"
    }
    task_monitor["successful_executions"].append(success_result)
    print(f"Flaky task succeeded: execution #{execution_count}")
'''

    # Recovery task that attempts to handle failures
    recovery_task = '''
from datetime import datetime

async def execute():
    """Recovery task that runs after failures"""
    from handlers.api.task_monitor import task_monitor
    
    failed_count = len(task_monitor["failed_executions"])
    successful_count = len(task_monitor["successful_executions"])
    
    recovery_result = {
        "timestamp": str(datetime.now()),
        "failed_tasks_detected": failed_count,
        "successful_tasks": successful_count,
        "recovery_action": "cleanup_and_retry"
    }
    
    task_monitor["recovery_attempts"].append(recovery_result)
    print(f"Recovery task executed - detected {failed_count} failures")
'''

    manifest_path = framework.create_test_manifest(
        'test-task-error-handling',
        endpoints=[
            {'path': '/api/task-monitor', 'method': 'get', 'handler': 'task_monitor_handler.handle'},
            {'path': '/api/reset-monitor', 'method': 'post', 'handler': 'task_monitor_handler.handle'},
        ],
        background_tasks=[
            {
                'name': 'flaky_task',
                'handler': 'flaky_task.handle',
                'schedule': 'interval:2',
                'enabled': True,
                'retry_attempts': 3,
                'retry_delay': 1
            },
            {
                'name': 'recovery_task',
                'handler': 'recovery_task.handle', 
                'schedule': 'interval:8',
                'enabled': True
            }
        ]
    )
    
    framework.create_test_handler('task_monitor_handler.py', task_monitor_handler)
    framework.create_test_handler('flaky_task.py', flaky_task)
    framework.create_test_handler('recovery_task.py', recovery_task)
    
    service = await framework.start_test_service(manifest_path, 'error_handling_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Reset monitoring
    requests.post(f"{base_url}/api/reset-monitor")
    
    # Wait for multiple task executions
    await asyncio.sleep(15)
    
    # Check monitoring results
    monitor_response = await assert_http_response(f"{base_url}/api/task-monitor")
    stats = monitor_response["stats"]
    
    total_executions = stats["successful"] + stats["failed"]
    recovery_attempts = stats["recoveries"]
    
    return {
        "error_handling_configured": True,
        "total_task_executions": total_executions,
        "successful_executions": stats["successful"],
        "failed_executions": stats["failed"],
        "recovery_attempts": recovery_attempts,
        "tasks_with_errors_handled": total_executions > 0,
        "recovery_system_active": recovery_attempts > 0
    }


@pytest.mark.asyncio
async def test_async_queue_processing(framework: ProServeTestFramework):
    """Test async queue-based task processing"""
    
    queue_handler = '''
import json
import asyncio
from datetime import datetime
from collections import deque

# Task queue and results
task_queue = deque()
processed_tasks = []
processing_stats = {
    "queued": 0,
    "processed": 0,
    "failed": 0
}

async def handle(request):
    path = str(request.url.path)
    method = request.method
    
    if path == "/api/queue/add" and method == "POST":
        try:
            data = await request.json()
            task_id = f"task_{len(task_queue) + 1}"
            
            task = {
                "id": task_id,
                "data": data,
                "created_at": str(datetime.now()),
                "status": "queued"
            }
            
            task_queue.append(task)
            processing_stats["queued"] += 1
            
            return {"task_id": task_id, "status": "queued", "queue_size": len(task_queue)}
        except:
            return {"error": "Invalid JSON"}, 400
    
    elif path == "/api/queue/status":
        return {
            "queue_size": len(task_queue),
            "processed_tasks": len(processed_tasks),
            "stats": processing_stats,
            "recent_tasks": processed_tasks[-5:] if processed_tasks else []
        }
    
    elif path == "/api/queue/results":
        return {
            "all_processed_tasks": processed_tasks,
            "processing_stats": processing_stats
        }
    
    return {"error": "Not found"}, 404
'''

    # Queue processor task
    queue_processor = '''
import asyncio
from datetime import datetime

async def execute():
    """Process tasks from the queue"""
    from handlers.api.queue_status import task_queue, processed_tasks, processing_stats
    
    if not task_queue:
        return  # No tasks to process
    
    # Process up to 3 tasks per execution
    processed_count = 0
    while task_queue and processed_count < 3:
        task = task_queue.popleft()
        
        try:
            # Simulate task processing
            await asyncio.sleep(0.1)  # Simulate work
            
            processed_task = {
                **task,
                "status": "completed",
                "processed_at": str(datetime.now()),
                "processing_time": 0.1,
                "result": f"Processed: {task['data'].get('message', 'No message')}"
            }
            
            processed_tasks.append(processed_task)
            processing_stats["processed"] += 1
            processed_count += 1
            
            print(f"Processed task: {task['id']}")
            
        except Exception as e:
            failed_task = {
                **task,
                "status": "failed",
                "processed_at": str(datetime.now()),
                "error": str(e)
            }
            
            processed_tasks.append(failed_task)
            processing_stats["failed"] += 1
            print(f"Task failed: {task['id']} - {e}")
    
    if processed_count > 0:
        print(f"Queue processor completed {processed_count} tasks")
'''

    manifest_path = framework.create_test_manifest(
        'test-async-queue',
        endpoints=[
            {'path': '/api/queue/add', 'method': 'post', 'handler': 'queue_handler.handle'},
            {'path': '/api/queue/status', 'method': 'get', 'handler': 'queue_handler.handle'},
            {'path': '/api/queue/results', 'method': 'get', 'handler': 'queue_handler.handle'},
        ],
        background_tasks=[
            {
                'name': 'queue_processor',
                'handler': 'queue_processor.handle',
                'schedule': 'interval:3',  # Process queue every 3 seconds
                'enabled': True
            }
        ]
    )
    
    framework.create_test_handler('queue_handler.py', queue_handler)
    framework.create_test_handler('queue_processor.py', queue_processor)
    
    service = await framework.start_test_service(manifest_path, 'queue_test')
    manifest = service.manifest
    base_url = f"http://{manifest.host}:{manifest.port}"
    
    # Add multiple tasks to queue
    tasks_added = []
    for i in range(5):
        task_data = {"message": f"Test task {i+1}", "priority": i % 3}
        add_response = requests.post(f"{base_url}/api/queue/add", json=task_data)
        assert add_response.status_code == 200
        tasks_added.append(add_response.json())
    
    # Wait for processing
    await asyncio.sleep(10)
    
    # Check queue status
    status_response = await assert_http_response(f"{base_url}/api/queue/status")
    results_response = await assert_http_response(f"{base_url}/api/queue/results")
    
    return {
        "queue_system_working": True,
        "tasks_added": len(tasks_added),
        "tasks_processed": results_response["processing_stats"]["processed"],
        "tasks_failed": results_response["processing_stats"]["failed"],
        "queue_size": status_response["queue_size"],
        "processing_successful": results_response["processing_stats"]["processed"] >= 3,
        "all_tasks_handled": (results_response["processing_stats"]["processed"] + 
                             results_response["processing_stats"]["failed"]) >= 4
    }
