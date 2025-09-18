"""
ProServe Mock System - Simplified and Modular
New streamlined mock system that replaces the legacy monolithic version

This file is now just a thin wrapper around the modular mock system.
The heavy lifting is done by the mocking/ package modules:
- mocking/mock_types.py - Mock system data structures and types
- mocking/mock_handler.py - Mock request processing and response generation
- mocking/mock_manager.py - Mock system management and coordination

Author: Tom Sapletta <info@softreck.dev>
License: Apache 2.0
"""

# Import the actual modular mock system components (fixed imports)
from .mocking import (
    MockResponse,
    MockEndpoint,
    MockService,
    MockRequest,
    MockRequestHandler,
    MockSystemManager,
    get_mock_system,
    reset_mock_system,
    generate_sample_user_data,
    generate_sample_product_data,
    generate_sample_order_data,
    create_error_response,
    create_success_response,
    create_paginated_response,
    create_mock_handler_for_service,
    create_mock_handler_for_endpoint
)

# Legacy compatibility - expose the main classes
__all__ = [
    'MockResponse',
    'MockEndpoint', 
    'MockService',
    'MockRequest',
    'MockRequestHandler',
    'MockSystemManager',
    'get_mock_system',
    'reset_mock_system',
    'generate_sample_user_data',
    'generate_sample_product_data',
    'generate_sample_order_data',
    'create_error_response',
    'create_success_response',
    'create_paginated_response',
    'create_mock_handler_for_service',
    'create_mock_handler_for_endpoint'
]

# Backward compatibility aliases for legacy code
MockType = MockResponse  # Alias for backward compatibility
MockRule = MockEndpoint  # Alias for backward compatibility
MockHandler = MockRequestHandler  # Alias for backward compatibility
ResponseGenerator = create_success_response  # Alias for backward compatibility
MockManager = MockSystemManager  # Alias for backward compatibility
MockRegistry = MockSystemManager  # Alias for backward compatibility
create_mock_service = create_mock_handler_for_service  # Alias for backward compatibility
register_mock_endpoint = create_mock_handler_for_endpoint  # Alias for backward compatibility
clear_all_mocks = reset_mock_system  # Alias for backward compatibility
