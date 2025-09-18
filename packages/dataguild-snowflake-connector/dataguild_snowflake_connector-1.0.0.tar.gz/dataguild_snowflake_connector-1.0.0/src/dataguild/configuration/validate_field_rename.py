"""
DataGuild configuration field rename validation.

This module provides utilities for handling renamed fields in Pydantic configuration
models, ensuring backward compatibility while encouraging users to migrate to
new field names.
"""

import logging
import warnings
from typing import Any, Callable, Optional, Union
import inspect

logger = logging.getLogger(__name__)


def pydantic_renamed_field(
        old_name: str,
        new_name: str,
        deprecated_in_version: Optional[str] = None,
        removal_version: Optional[str] = None,
        migration_guide_url: Optional[str] = None
) -> Callable:
    """
    Create a property that provides backward compatibility for renamed fields.

    This function creates a property that issues a deprecation warning when
    accessed and returns the value of the new field. This allows for smooth
    migration from old field names to new ones while maintaining backward
    compatibility.

    Args:
        old_name: The old (deprecated) field name
        new_name: The new field name that should be used
        deprecated_in_version: Optional version when the field was deprecated
        removal_version: Optional version when the field will be removed
        migration_guide_url: Optional URL to migration documentation

    Returns:
        Property that warns and returns the new field's value

    Examples:
        >>> class MyConfig(BaseModel):
        ...     # New field name
        ...     connection_timeout: int = 30
        ...
        ...     # Old field name for backward compatibility
        ...     timeout = pydantic_renamed_field(
        ...         "timeout",
        ...         "connection_timeout",
        ...         deprecated_in_version="1.5.0",
        ...         removal_version="2.0.0"
        ...     )
        >>>
        >>> config = MyConfig()
        >>> config.connection_timeout  # Preferred way
        30
        >>> config.timeout  # Works but issues warning
        UserWarning: Field 'timeout' has been renamed to 'connection_timeout'...
        30
    """

    def _renamed_field_getter(self) -> Any:
        """Getter that returns the new field's value with a deprecation warning."""
        # Build warning message
        warning_parts = [f"Field '{old_name}' has been renamed to '{new_name}'."]

        if deprecated_in_version:
            warning_parts.append(f"Deprecated in version {deprecated_in_version}.")

        if removal_version:
            warning_parts.append(f"Will be removed in version {removal_version}.")

        warning_parts.append("Please update your configuration.")

        if migration_guide_url:
            warning_parts.append(f"See migration guide: {migration_guide_url}")

        warning_message = " ".join(warning_parts)

        # Issue deprecation warning
        warnings.warn(
            warning_message,
            DeprecationWarning,
            stacklevel=2
        )

        # Log the usage for monitoring
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_info = f"{frame.f_back.f_code.co_filename}:{frame.f_back.f_lineno}"
            logger.info(f"Deprecated field '{old_name}' accessed from {caller_info}")

        # Return the value of the new field
        try:
            return getattr(self, new_name)
        except AttributeError:
            raise AttributeError(
                f"Cannot access renamed field '{old_name}': "
                f"new field '{new_name}' does not exist on this object"
            )

    def _renamed_field_setter(self, value: Any) -> None:
        """Setter that sets the new field's value with a deprecation warning."""
        # Build warning message for setter
        warning_parts = [f"Setting field '{old_name}' is deprecated."]
        warning_parts.append(f"Please use '{new_name}' instead.")

        if deprecated_in_version:
            warning_parts.append(f"Deprecated in version {deprecated_in_version}.")

        if removal_version:
            warning_parts.append(f"Will be removed in version {removal_version}.")

        warning_message = " ".join(warning_parts)

        # Issue deprecation warning
        warnings.warn(
            warning_message,
            DeprecationWarning,
            stacklevel=2
        )

        # Set the value on the new field
        try:
            setattr(self, new_name, value)
        except AttributeError:
            raise AttributeError(
                f"Cannot set renamed field '{old_name}': "
                f"new field '{new_name}' does not exist on this object"
            )

    return property(_renamed_field_getter, _renamed_field_setter)


def pydantic_renamed_field_simple(old_name: str, new_name: str) -> Callable:
    """
    Simplified version of pydantic_renamed_field for basic use cases.

    This is a convenience function for cases where you only need to specify
    the old and new field names without version information.

    Args:
        old_name: The old (deprecated) field name
        new_name: The new field name that should be used

    Returns:
        Property that warns and returns the new field's value

    Examples:
        >>> class MyConfig(BaseModel):
        ...     new_field: str = "value"
        ...     old_field = pydantic_renamed_field_simple("old_field", "new_field")
    """
    return pydantic_renamed_field(old_name, new_name)


def create_renamed_field_warning(
        old_name: str,
        new_name: str,
        deprecated_in_version: Optional[str] = None,
        removal_version: Optional[str] = None
) -> str:
    """
    Create a standardized warning message for renamed fields.

    This utility function helps create consistent warning messages
    for renamed fields across different parts of the DataGuild codebase.

    Args:
        old_name: The old field name
        new_name: The new field name
        deprecated_in_version: Optional version when field was deprecated
        removal_version: Optional version when field will be removed

    Returns:
        Formatted warning message

    Examples:
        >>> warning = create_renamed_field_warning(
        ...     "timeout",
        ...     "connection_timeout",
        ...     "1.5.0",
        ...     "2.0.0"
        ... )
        >>> print(warning)
        Field 'timeout' has been renamed to 'connection_timeout'. Deprecated in version 1.5.0. Will be removed in version 2.0.0.
    """
    warning_parts = [f"Field '{old_name}' has been renamed to '{new_name}'."]

    if deprecated_in_version:
        warning_parts.append(f"Deprecated in version {deprecated_in_version}.")

    if removal_version:
        warning_parts.append(f"Will be removed in version {removal_version}.")

    return " ".join(warning_parts)


def validate_renamed_field_usage(config_dict: dict, renamed_fields: dict) -> list:
    """
    Validate configuration dictionary for usage of renamed fields.

    This function checks for the presence of renamed fields in a configuration
    dictionary and returns information about deprecated field usage.

    Args:
        config_dict: Configuration dictionary to validate
        renamed_fields: Dictionary mapping old field names to new field names

    Returns:
        List of tuples containing (old_name, new_name) for found renamed fields

    Examples:
        >>> renamed_fields = {"old_timeout": "connection_timeout", "old_port": "server_port"}
        >>> config = {"connection_timeout": 30, "old_port": 8080}
        >>> deprecated = validate_renamed_field_usage(config, renamed_fields)
        >>> print(deprecated)
        [('old_port', 'server_port')]
    """
    found_renamed = []

    for old_name, new_name in renamed_fields.items():
        if old_name in config_dict:
            found_renamed.append((old_name, new_name))

    return found_renamed


def migrate_renamed_fields(config_dict: dict, renamed_fields: dict, warn: bool = True) -> dict:
    """
    Migrate a configuration dictionary by replacing old field names with new ones.

    This function creates a new configuration dictionary with old field names
    replaced by their new counterparts. Optionally issues warnings about
    the deprecated field usage.

    Args:
        config_dict: Original configuration dictionary
        renamed_fields: Dictionary mapping old field names to new field names
        warn: Whether to issue warnings for renamed fields found

    Returns:
        New configuration dictionary with updated field names

    Examples:
        >>> renamed_fields = {"old_timeout": "connection_timeout"}
        >>> old_config = {"old_timeout": 30, "other_field": "value"}
        >>> new_config = migrate_renamed_fields(old_config, renamed_fields)
        >>> print(new_config)
        {'connection_timeout': 30, 'other_field': 'value'}
    """
    migrated_config = config_dict.copy()

    for old_name, new_name in renamed_fields.items():
        if old_name in migrated_config:
            # Move value from old field to new field
            value = migrated_config.pop(old_name)

            # Only set new field if it doesn't already exist
            if new_name not in migrated_config:
                migrated_config[new_name] = value

            if warn:
                warning_message = create_renamed_field_warning(old_name, new_name)
                warnings.warn(warning_message, DeprecationWarning, stacklevel=2)

    return migrated_config


class RenamedFieldDescriptor:
    """
    Descriptor class for more advanced renamed field handling.

    This descriptor provides more control over renamed field behavior,
    including custom warning messages and migration logic.
    """

    def __init__(
            self,
            old_name: str,
            new_name: str,
            deprecated_in_version: Optional[str] = None,
            removal_version: Optional[str] = None,
            custom_warning_message: Optional[str] = None
    ):
        """
        Initialize the renamed field descriptor.

        Args:
            old_name: The old field name
            new_name: The new field name
            deprecated_in_version: Optional version when deprecated
            removal_version: Optional version when it will be removed
            custom_warning_message: Optional custom warning message
        """
        self.old_name = old_name
        self.new_name = new_name
        self.deprecated_in_version = deprecated_in_version
        self.removal_version = removal_version
        self.custom_warning_message = custom_warning_message

    def __get__(self, obj, objtype=None):
        """Handle field access."""
        if obj is None:
            return self

        # Issue warning
        if self.custom_warning_message:
            warning_message = self.custom_warning_message
        else:
            warning_message = create_renamed_field_warning(
                self.old_name,
                self.new_name,
                self.deprecated_in_version,
                self.removal_version
            )

        warnings.warn(warning_message, DeprecationWarning, stacklevel=2)

        # Return value from new field
        return getattr(obj, self.new_name)

    def __set__(self, obj, value):
        """Handle field assignment."""
        # Issue warning for setter
        warning_message = f"Setting '{self.old_name}' is deprecated. Use '{self.new_name}' instead."
        warnings.warn(warning_message, DeprecationWarning, stacklevel=2)

        # Set value on new field
        setattr(obj, self.new_name, value)


# Export all functions and classes
__all__ = [
    'pydantic_renamed_field',
    'pydantic_renamed_field_simple',
    'create_renamed_field_warning',
    'validate_renamed_field_usage',
    'migrate_renamed_fields',
    'RenamedFieldDescriptor',
]

# Example usage and testing (for development purposes)
if __name__ == "__main__":
    from pydantic import BaseModel
    import warnings

    print("=== DataGuild Field Rename Validation Examples ===\n")

    # Capture warnings for demonstration
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")


        # Example 1: Basic renamed field
        class ExampleConfig(BaseModel):
            connection_timeout: int = 30
            server_port: int = 8080

            # Old field names for backward compatibility
            timeout = pydantic_renamed_field(
                "timeout",
                "connection_timeout",
                deprecated_in_version="1.5.0",
                removal_version="2.0.0",
                migration_guide_url="https://docs.dataguild.com/migration"
            )

            port = pydantic_renamed_field_simple("port", "server_port")


        print("Example 1: Testing renamed field access")
        config = ExampleConfig()

        print(f"New field (connection_timeout): {config.connection_timeout}")
        print(f"Old field (timeout): {config.timeout}")  # Should warn

        print(f"New field (server_port): {config.server_port}")
        print(f"Old field (port): {config.port}")  # Should warn

        # Test setter
        config.timeout = 60  # Should warn
        print(f"After setting old field, new field value: {config.connection_timeout}")

        print()

        # Example 2: Configuration migration
        print("Example 2: Configuration migration")
        old_config = {
            "timeout": 30,
            "port": 8080,
            "new_field": "value"
        }

        renamed_fields = {
            "timeout": "connection_timeout",
            "port": "server_port"
        }

        print(f"Original config: {old_config}")
        migrated_config = migrate_renamed_fields(old_config, renamed_fields)
        print(f"Migrated config: {migrated_config}")

        print()

        # Example 3: Validation
        print("Example 3: Renamed field validation")
        deprecated_usage = validate_renamed_field_usage(old_config, renamed_fields)
        print(f"Found deprecated fields: {deprecated_usage}")

        # Show captured warnings
        print(f"\nCaptured {len(caught_warnings)} warnings:")
        for warning in caught_warnings:
            print(f"  - {warning.message}")
