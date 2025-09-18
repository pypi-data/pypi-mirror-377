"""
ProServe AutoTest Module
Automatic testing functionality that runs after service startup
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from aiohttp import ClientSession, ClientTimeout
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class AutoTestConfig:
    """Configuration for automatic testing"""
    enabled: bool = True
    delay_seconds: int = 5  # Wait after startup before testing
    timeout_seconds: int = 30
    retry_count: int = 3
    retry_delay: int = 2
    endpoints_to_test: List[str] = field(default_factory=list)
    custom_tests: List[Dict] = field(default_factory=list)
    health_check: bool = True
    metrics_check: bool = True
    report_format: str = "json"  # json, text, structured


@dataclass
class AutoTestResult:
    """Result of automatic test execution"""
    test_name: str
    success: bool
    response_time_ms: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))


class AutoTester:
    """Automatic testing engine for ProServe services"""
    
    def __init__(self, config: AutoTestConfig, service_host: str = "localhost", service_port: int = 8080, use_tls: bool = False):
        self.config = config
        self.service_host = service_host
        self.service_port = service_port
        self.protocol = "https" if use_tls else "http"
        self.base_url = f"{self.protocol}://{service_host}:{service_port}"
        self.results: List[AutoTestResult] = []
        
    async def run_autotests(self) -> List[AutoTestResult]:
        """Run all configured automatic tests"""
        if not self.config.enabled:
            logger.info("AutoTesting disabled - skipping tests")
            return []
            
        logger.info(f"Starting autotests in {self.config.delay_seconds} seconds...")
        await asyncio.sleep(self.config.delay_seconds)
        
        logger.info(f"Running autotests for {self.base_url}")
        self.results = []
        
        timeout = ClientTimeout(total=self.config.timeout_seconds)
        connector_kwargs = {}
        
        # Handle self-signed certificates for TLS testing
        if self.protocol == "https":
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector_kwargs['ssl'] = ssl_context
            
        async with ClientSession(timeout=timeout, connector_kwargs=connector_kwargs) as session:
            # Test health endpoint
            if self.config.health_check:
                await self._test_endpoint(session, "/health", "Health Check")
                
            # Test metrics endpoint  
            if self.config.metrics_check:
                await self._test_endpoint(session, "/metrics", "Metrics Check")
                
            # Test configured endpoints
            for endpoint in self.config.endpoints_to_test:
                await self._test_endpoint(session, endpoint, f"Endpoint Test: {endpoint}")
                
            # Run custom tests
            for custom_test in self.config.custom_tests:
                await self._run_custom_test(session, custom_test)
                
        await self._report_results()
        return self.results
        
    async def _test_endpoint(self, session: ClientSession, endpoint: str, test_name: str):
        """Test a single endpoint with retry logic"""
        for attempt in range(self.config.retry_count):
            try:
                start_time = time.time()
                url = f"{self.base_url}{endpoint}"
                
                logger.info(f"Testing {test_name}: {url} (attempt {attempt + 1}/{self.config.retry_count})")
                
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    try:
                        response_data = await response.json()
                    except:
                        response_data = {"text": await response.text()}
                    
                    result = AutoTestResult(
                        test_name=test_name,
                        success=response.status < 400,
                        response_time_ms=round(response_time, 2),
                        status_code=response.status,
                        response_data=response_data
                    )
                    
                    self.results.append(result)
                    
                    if result.success:
                        logger.info(f"✅ {test_name} passed ({response.status}) in {result.response_time_ms}ms")
                        return
                    else:
                        logger.warning(f"⚠️ {test_name} failed with status {response.status}")
                        
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"❌ {test_name} error (attempt {attempt + 1}): {error_msg}")
                
                if attempt == self.config.retry_count - 1:  # Last attempt
                    result = AutoTestResult(
                        test_name=test_name,
                        success=False,
                        response_time_ms=0,
                        error_message=error_msg
                    )
                    self.results.append(result)
                else:
                    await asyncio.sleep(self.config.retry_delay)
                    
    async def _run_custom_test(self, session: ClientSession, test_config: Dict):
        """Run a custom test configuration"""
        test_name = test_config.get("name", "Custom Test")
        method = test_config.get("method", "GET").upper()
        endpoint = test_config.get("endpoint", "/")
        expected_status = test_config.get("expected_status", 200)
        expected_data = test_config.get("expected_data")
        
        try:
            start_time = time.time()
            url = f"{self.base_url}{endpoint}"
            
            logger.info(f"Running custom test: {test_name}")
            
            if method == "GET":
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json() if response.content_type == "application/json" else await response.text()
            elif method == "POST":
                data = test_config.get("data", {})
                async with session.post(url, json=data) as response:
                    response_time = (time.time() - start_time) * 1000  
                    response_data = await response.json() if response.content_type == "application/json" else await response.text()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            # Check expected status
            status_ok = response.status == expected_status
            
            # Check expected data if specified
            data_ok = True
            if expected_data and isinstance(response_data, dict):
                for key, expected_value in expected_data.items():
                    if response_data.get(key) != expected_value:
                        data_ok = False
                        break
                        
            success = status_ok and data_ok
            
            result = AutoTestResult(
                test_name=test_name,
                success=success,
                response_time_ms=round(response_time, 2),
                status_code=response.status,
                response_data=response_data if isinstance(response_data, dict) else {"response": response_data}
            )
            
            self.results.append(result)
            
            if success:
                logger.info(f"✅ {test_name} passed")
            else:
                logger.warning(f"⚠️ {test_name} failed - status: {response.status}, data_match: {data_ok}")
                
        except Exception as e:
            logger.error(f"❌ Custom test {test_name} failed: {str(e)}")
            result = AutoTestResult(
                test_name=test_name,
                success=False,
                response_time_ms=0,
                error_message=str(e)
            )
            self.results.append(result)
            
    async def _report_results(self):
        """Generate and log test results report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Summary report
        logger.info("🔍 AutoTest Results Summary")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   ✅ Passed: {passed_tests}")
        logger.info(f"   ❌ Failed: {failed_tests}")
        logger.info(f"   📊 Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        if self.config.report_format == "structured":
            for result in self.results:
                status = "✅" if result.success else "❌"
                logger.info(f"   {status} {result.test_name}: {result.response_time_ms}ms")
                if not result.success and result.error_message:
                    logger.info(f"      Error: {result.error_message}")
                    
        elif self.config.report_format == "json":
            report_data = {
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": round(success_rate, 1)
                },
                "results": [
                    {
                        "test": r.test_name,
                        "success": r.success,
                        "response_time_ms": r.response_time_ms,
                        "status_code": r.status_code,
                        "error": r.error_message,
                        "timestamp": r.timestamp
                    } for r in self.results
                ]
            }
            logger.info("📋 Detailed JSON Report", extra={"autotest_report": report_data})


def create_autotest_config(manifest_data: Dict) -> AutoTestConfig:
    """Create AutoTestConfig from manifest data"""
    autotest_config = manifest_data.get("autotest", {})
    
    if isinstance(autotest_config, bool):
        return AutoTestConfig(enabled=autotest_config)
        
    return AutoTestConfig(
        enabled=autotest_config.get("enabled", True),
        delay_seconds=autotest_config.get("delay_seconds", 5),
        timeout_seconds=autotest_config.get("timeout_seconds", 30),
        retry_count=autotest_config.get("retry_count", 3),
        retry_delay=autotest_config.get("retry_delay", 2),
        endpoints_to_test=autotest_config.get("endpoints_to_test", []),
        custom_tests=autotest_config.get("custom_tests", []),
        health_check=autotest_config.get("health_check", True),
        metrics_check=autotest_config.get("metrics_check", True),
        report_format=autotest_config.get("report_format", "json")
    )
