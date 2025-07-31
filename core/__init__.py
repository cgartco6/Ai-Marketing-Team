"""
AI Marketing Team - Core Module

This module contains the fundamental components and utilities for the AI Marketing Team system.
It provides security, communication, and utility functions used by all agents.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "Proprietary"

# Import key components to make them available at package level
from .crypto import MilitaryCrypto
from .utils import (
    logger,
    secure_fetch,
    hash_data,
    PerformanceTimer,
    RateLimiter,
    DataSanitizer,
    ThreadSafeQueue,
    setup_directories,
    validate_config,
    ooda_cycle,
    get_system_info
)

# Define public API
__all__ = [
    'MilitaryCrypto',
    'logger',
    'secure_fetch',
    'hash_data',
    'PerformanceTimer',
    'RateLimiter',
    'DataSanitizer',
    'ThreadSafeQueue',
    'setup_directories',
    'validate_config',
    'ooda_cycle',
    'get_system_info'
]

# Package initialization
def init_package():
    """Initialize core package components"""
    setup_directories()
    
    if not validate_config():
        raise RuntimeError("Configuration validation failed")
    
    logger("Core package initialized successfully")

# Run initialization when package is imported
init_package()

# Clean up namespace
del init_package
