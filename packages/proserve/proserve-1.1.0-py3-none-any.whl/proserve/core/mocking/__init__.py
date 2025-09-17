"""
ProServe Mock System - Modular Mock System Components
Refactored from monolithic mock_system.py into focused, testable mock modules
"""

from .mock_types import (
    MockResponse, MockEndpoint, MockService, MockRequest,
    generate_sample_user_data, generate_sample_product_data, generate_sample_order_data,
    create_error_response, create_success_response, create_paginated_response
)
from .mock_handler import (
    MockRequestHandler, create_mock_handler_for_service, create_mock_handler_for_endpoint
)
from .mock_manager import (
    MockSystemManager, get_mock_system, reset_mock_system
)

__all__ = [
    # Core Types
    'MockResponse', 'MockEndpoint', 'MockService', 'MockRequest',
    
    # Data Generation Utilities
    'generate_sample_user_data', 'generate_sample_product_data', 'generate_sample_order_data',
    'create_error_response', 'create_success_response', 'create_paginated_response',
    
    # Request Handling
    'MockRequestHandler', 'create_mock_handler_for_service', 'create_mock_handler_for_endpoint',
    
    # System Management
    'MockSystemManager', 'get_mock_system', 'reset_mock_system'
]

# Backward compatibility exports
MockSystemManager = MockSystemManager
MockResponse = MockResponse
MockEndpoint = MockEndpoint
MockService = MockService
