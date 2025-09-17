"""
ProServe Test Runner
Main test execution engine with HTML reports, CI/CD integration, and automation
"""

import asyncio
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import xml.etree.ElementTree as ET

from .test_framework import ProServeTestFramework, TestResult, TestSuite
from .test_core import core_test_suite
from .test_grpc import grpc_test_suite
from .test_sdk import sdk_test_suite
from .test_migration import migration_test_suite


class TestRunner:
    """Main test runner for ProServe E2E tests"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path('test_reports')
        self.output_dir.mkdir(exist_ok=True)
        self.start_time = None
        self.end_time = None
        self.results = {}
        self.framework = None
    
    async def run_all_suites(self, 
                           parallel: bool = False,
                           include_suites: List[str] = None,
                           exclude_suites: List[str] = None,
                           verbose: bool = True) -> Dict[str, Any]:
        """Run all test suites and generate comprehensive reports"""
        
        self.start_time = datetime.now()
        print(f"🚀 Starting ProServe E2E Test Suite at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize test framework
        self.framework = ProServeTestFramework(verbose=verbose)
        
        # Define all available test suites
        all_suites = {
            'core': core_test_suite,
            'grpc': grpc_test_suite,
            'sdk': sdk_test_suite,
            'migration': migration_test_suite
        }
        
        # Filter suites based on include/exclude
        suites_to_run = {}
        for name, suite in all_suites.items():
            if include_suites and name not in include_suites:
                continue
            if exclude_suites and name in exclude_suites:
                continue
            suites_to_run[name] = suite
        
        print(f"📋 Running {len(suites_to_run)} test suites: {', '.join(suites_to_run.keys())}")
        
        # Run test suites
        if parallel and len(suites_to_run) > 1:
            # Run suites in parallel
            tasks = []
            for name, suite in suites_to_run.items():
                task = asyncio.create_task(self._run_suite(name, suite))
                tasks.append(task)
            
            suite_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, (name, suite) in enumerate(suites_to_run.items()):
                result = suite_results[i]
                if isinstance(result, Exception):
                    self.results[name] = {
                        'success': False,
                        'error': str(result),
                        'tests': [],
                        'duration': 0
                    }
                else:
                    self.results[name] = result
        else:
            # Run suites sequentially
            for name, suite in suites_to_run.items():
                self.results[name] = await self._run_suite(name, suite)
        
        self.end_time = datetime.now()
        
        # Generate reports
        await self._generate_reports()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    async def _run_suite(self, name: str, suite: TestSuite) -> Dict[str, Any]:
        """Run a single test suite"""
        print(f"\n🧪 Running {name} test suite...")
        
        try:
            suite_result = await self.framework.run_test_suite(suite)
            
            return {
                'success': suite_result.success,
                'tests': [self._serialize_test_result(test) for test in suite_result.test_results],
                'duration': suite_result.duration.total_seconds(),
                'passed': suite_result.passed_count,
                'failed': suite_result.failed_count,
                'errors': suite_result.errors,
                'setup_success': suite_result.setup_success,
                'teardown_success': suite_result.teardown_success
            }
        except Exception as e:
            print(f"❌ Error running {name} suite: {e}")
            return {
                'success': False,
                'error': str(e),
                'tests': [],
                'duration': 0,
                'passed': 0,
                'failed': 0
            }
    
    def _serialize_test_result(self, result: TestResult) -> Dict[str, Any]:
        """Convert TestResult to serializable dict"""
        return {
            'name': result.test_name,
            'success': result.success,
            'duration': result.duration.total_seconds() if result.duration else 0,
            'output': result.output,
            'error': result.error
        }
    
    async def _generate_reports(self):
        """Generate all report formats"""
        print(f"\n📊 Generating test reports in {self.output_dir}...")
        
        # Generate JSON report
        await self._generate_json_report()
        
        # Generate HTML report
        await self._generate_html_report()
        
        # Generate JUnit XML report
        await self._generate_junit_report()
        
        # Generate CI summary
        await self._generate_ci_summary()
    
    async def _generate_json_report(self):
        """Generate JSON test report"""
        report_data = {
            'timestamp': self.start_time.isoformat(),
            'duration': (self.end_time - self.start_time).total_seconds(),
            'summary': self._get_summary_stats(),
            'suites': self.results,
            'environment': {
                'python_version': sys.version,
                'platform': sys.platform,
                'test_framework': 'ProServe E2E'
            }
        }
        
        json_file = self.output_dir / 'test_results.json'
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"✅ JSON report: {json_file}")
    
    async def _generate_html_report(self):
        """Generate HTML test report"""
        html_content = self._create_html_report()
        
        html_file = self.output_dir / 'test_report.html'
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"✅ HTML report: {html_file}")
    
    async def _generate_junit_report(self):
        """Generate JUnit XML report for CI/CD systems"""
        root = ET.Element('testsuites')
        root.set('name', 'ProServe E2E Tests')
        root.set('time', str((self.end_time - self.start_time).total_seconds()))
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for suite_name, suite_result in self.results.items():
            testsuite = ET.SubElement(root, 'testsuite')
            testsuite.set('name', suite_name)
            testsuite.set('time', str(suite_result.get('duration', 0)))
            
            suite_tests = suite_result.get('tests', [])
            testsuite.set('tests', str(len(suite_tests)))
            
            suite_failures = sum(1 for test in suite_tests if not test['success'] and not test.get('error'))
            suite_errors = sum(1 for test in suite_tests if test.get('error'))
            
            testsuite.set('failures', str(suite_failures))
            testsuite.set('errors', str(suite_errors))
            
            total_tests += len(suite_tests)
            total_failures += suite_failures
            total_errors += suite_errors
            
            for test in suite_tests:
                testcase = ET.SubElement(testsuite, 'testcase')
                testcase.set('name', test['name'])
                testcase.set('time', str(test['duration']))
                testcase.set('classname', f"{suite_name}.{test['name']}")
                
                if not test['success']:
                    if test.get('error'):
                        error = ET.SubElement(testcase, 'error')
                        error.set('message', test['error'])
                        error.text = str(test.get('output', ''))
                    else:
                        failure = ET.SubElement(testcase, 'failure')
                        failure.set('message', 'Test failed')
                        failure.text = str(test.get('output', ''))
        
        root.set('tests', str(total_tests))
        root.set('failures', str(total_failures))
        root.set('errors', str(total_errors))
        
        junit_file = self.output_dir / 'junit_results.xml'
        tree = ET.ElementTree(root)
        tree.write(junit_file, encoding='utf-8', xml_declaration=True)
        
        print(f"✅ JUnit XML report: {junit_file}")
    
    async def _generate_ci_summary(self):
        """Generate CI/CD summary file"""
        summary = self._get_summary_stats()
        
        # GitHub Actions summary format
        if 'GITHUB_ACTIONS' in __import__('os').environ:
            await self._generate_github_summary(summary)
        
        # Generic CI summary
        ci_file = self.output_dir / 'ci_summary.txt'
        with open(ci_file, 'w') as f:
            f.write(f"ProServe E2E Test Results\n")
            f.write(f"========================\n\n")
            f.write(f"Total Suites: {summary['total_suites']}\n")
            f.write(f"Total Tests: {summary['total_tests']}\n")
            f.write(f"Passed: {summary['passed_tests']}\n")
            f.write(f"Failed: {summary['failed_tests']}\n")
            f.write(f"Success Rate: {summary['success_rate']:.1f}%\n")
            f.write(f"Duration: {summary['duration']:.2f}s\n\n")
            
            if summary['failed_tests'] > 0:
                f.write("Failed Tests:\n")
                for suite_name, suite_result in self.results.items():
                    for test in suite_result.get('tests', []):
                        if not test['success']:
                            f.write(f"- {suite_name}.{test['name']}: {test.get('error', 'Failed')}\n")
        
        print(f"✅ CI summary: {ci_file}")
    
    async def _generate_github_summary(self, summary: Dict[str, Any]):
        """Generate GitHub Actions job summary"""
        github_summary = f"""
# ProServe E2E Test Results

## Summary
- **Total Suites:** {summary['total_suites']}
- **Total Tests:** {summary['total_tests']}
- **Passed:** {summary['passed_tests']} ✅
- **Failed:** {summary['failed_tests']} ❌
- **Success Rate:** {summary['success_rate']:.1f}%
- **Duration:** {summary['duration']:.2f}s

## Suite Results
"""
        
        for suite_name, suite_result in self.results.items():
            status = "✅" if suite_result['success'] else "❌"
            github_summary += f"- **{suite_name}:** {status} ({suite_result.get('passed', 0)}/{len(suite_result.get('tests', []))} passed)\n"
        
        if summary['failed_tests'] > 0:
            github_summary += "\n## Failed Tests\n"
            for suite_name, suite_result in self.results.items():
                for test in suite_result.get('tests', []):
                    if not test['success']:
                        github_summary += f"- `{suite_name}.{test['name']}`: {test.get('error', 'Failed')}\n"
        
        # Write to GitHub Actions summary
        github_summary_file = Path(__import__('os').environ.get('GITHUB_STEP_SUMMARY', 'github_summary.md'))
        with open(github_summary_file, 'w') as f:
            f.write(github_summary)
    
    def _create_html_report(self) -> str:
        """Create comprehensive HTML report"""
        summary = self._get_summary_stats()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProServe E2E Test Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-card.success {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .stat-card.failure {{ background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
        .suite {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }}
        .suite-header {{ background: #ecf0f1; padding: 15px; font-weight: bold; cursor: pointer; }}
        .suite-header.success {{ background: #d5edda; }}
        .suite-header.failure {{ background: #f8d7da; }}
        .suite-content {{ padding: 15px; display: none; }}
        .test {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; background: #f9f9f9; }}
        .test.success {{ border-left-color: #28a745; }}
        .test.failure {{ border-left-color: #dc3545; }}
        .test-name {{ font-weight: bold; }}
        .test-duration {{ color: #666; font-size: 0.9em; }}
        .test-error {{ color: #dc3545; font-family: monospace; font-size: 0.8em; margin-top: 5px; }}
        .progress-bar {{ background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden; margin: 20px 0; }}
        .progress-fill {{ background: linear-gradient(90deg, #28a745, #20c997); height: 100%; transition: width 0.3s ease; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        .toggle {{ cursor: pointer; user-select: none; }}
        .toggle:hover {{ background: #f8f9fa; }}
    </style>
    <script>
        function toggleSuite(element) {{
            const content = element.nextElementSibling;
            content.style.display = content.style.display === 'none' ? 'block' : 'none';
        }}
        
        window.onload = function() {{
            // Auto-expand failed suites
            document.querySelectorAll('.suite-header.failure').forEach(header => {{
                header.nextElementSibling.style.display = 'block';
            }});
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>🧪 ProServe E2E Test Report</h1>
        
        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            Duration: {summary['duration']:.2f}s
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-value">{summary['total_suites']}</div>
                <div class="stat-label">Test Suites</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{summary['total_tests']}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card success">
                <div class="stat-value">{summary['passed_tests']}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card failure">
                <div class="stat-value">{summary['failed_tests']}</div>
                <div class="stat-label">Failed</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {summary['success_rate']}%"></div>
        </div>
        <div style="text-align: center; margin: 10px 0;">
            <strong>Success Rate: {summary['success_rate']:.1f}%</strong>
        </div>
        
        <h2>Test Suites</h2>
"""
        
        # Add suite details
        for suite_name, suite_result in self.results.items():
            suite_success = suite_result.get('success', False)
            suite_class = 'success' if suite_success else 'failure'
            suite_status = '✅' if suite_success else '❌'
            
            html += f"""
        <div class="suite">
            <div class="suite-header {suite_class} toggle" onclick="toggleSuite(this)">
                {suite_status} {suite_name.title()} Suite 
                ({suite_result.get('passed', 0)}/{len(suite_result.get('tests', []))} passed, 
                {suite_result.get('duration', 0):.2f}s)
            </div>
            <div class="suite-content">
"""
            
            # Add test details
            for test in suite_result.get('tests', []):
                test_success = test.get('success', False)
                test_class = 'success' if test_success else 'failure'
                test_status = '✅' if test_success else '❌'
                
                html += f"""
                <div class="test {test_class}">
                    <div class="test-name">{test_status} {test['name']}</div>
                    <div class="test-duration">Duration: {test['duration']:.3f}s</div>
"""
                
                if not test_success and test.get('error'):
                    html += f'<div class="test-error">Error: {test["error"]}</div>'
                
                html += '</div>'
            
            html += '</div></div>'
        
        html += """
    </div>
</body>
</html>"""
        
        return html
    
    def _get_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics"""
        total_suites = len(self.results)
        total_tests = sum(len(suite.get('tests', [])) for suite in self.results.values())
        passed_tests = sum(suite.get('passed', 0) for suite in self.results.values())
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        return {
            'total_suites': total_suites,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'duration': duration
        }
    
    def _print_summary(self):
        """Print test execution summary"""
        summary = self._get_summary_stats()
        
        print(f"\n{'='*60}")
        print(f"🏁 ProServe E2E Test Summary")
        print(f"{'='*60}")
        print(f"Suites Run: {summary['total_suites']}")
        print(f"Tests Run: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']} ✅")
        print(f"Failed: {summary['failed_tests']} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Duration: {summary['duration']:.2f}s")
        print(f"Reports: {self.output_dir.absolute()}")
        
        if summary['failed_tests'] > 0:
            print(f"\n❌ Failed Tests:")
            for suite_name, suite_result in self.results.items():
                for test in suite_result.get('tests', []):
                    if not test['success']:
                        error_msg = test.get('error', 'Failed')[:80]
                        print(f"  - {suite_name}.{test['name']}: {error_msg}")
        
        print(f"{'='*60}\n")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='ProServe E2E Test Runner')
    parser.add_argument('--parallel', action='store_true', 
                       help='Run test suites in parallel')
    parser.add_argument('--include', nargs='+', 
                       choices=['core', 'grpc', 'sdk', 'migration'],
                       help='Include only specified test suites')
    parser.add_argument('--exclude', nargs='+',
                       choices=['core', 'grpc', 'sdk', 'migration'],
                       help='Exclude specified test suites')
    parser.add_argument('--output', type=Path, default=Path('test_reports'),
                       help='Output directory for reports')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--ci', action='store_true',
                       help='CI mode - exit with error code on test failures')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(output_dir=args.output)
    
    try:
        # Run tests
        results = await runner.run_all_suites(
            parallel=args.parallel,
            include_suites=args.include,
            exclude_suites=args.exclude,
            verbose=args.verbose
        )
        
        # Check for failures in CI mode
        if args.ci:
            summary = runner._get_summary_stats()
            if summary['failed_tests'] > 0:
                print(f"❌ Test failures detected in CI mode")
                sys.exit(1)
        
        print(f"✅ Test execution completed successfully")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        if args.ci:
            sys.exit(1)
        raise


if __name__ == '__main__':
    asyncio.run(main())
