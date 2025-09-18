"""
DataGuild Configuration Package
This package contains common configuration utilities, patterns, and base classes
used throughout the DataGuild platform for consistent configuration management.
"""

from dataguild.configuration.common import (
    ConfigModel,
    AllowDenyPattern,
    DynamicTypedConfig,
    ConfigurationError,
    validate_config,
    merge_configs,
)

from dataguild.configuration.pattern_utils import (
    UUID_REGEX,
    EMAIL_REGEX,
    SNOWFLAKE_IDENTIFIER_REGEX,
)

__all__ = [
    'ConfigModel',
    'AllowDenyPattern', 
    'DynamicTypedConfig',
    'ConfigurationError',
    'validate_config',
    'merge_configs',
    'UUID_REGEX',
    'EMAIL_REGEX',
    'SNOWFLAKE_IDENTIFIER_REGEX',
]
