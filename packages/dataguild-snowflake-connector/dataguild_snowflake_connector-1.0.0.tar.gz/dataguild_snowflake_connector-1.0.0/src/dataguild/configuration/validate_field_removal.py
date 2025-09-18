"""
DataGuild configuration field removal validation.

This module provides utilities for handling removed fields in Pydantic configuration
models, ensuring graceful degradation and clear error messages when deprecated
fields are accessed.
"""

import logging
from typing import Any, Callable, Optional
import inspect

logger = logging.getLogger(__name__)


def pydantic_removed_field(
        reason: str,
        removed_in_version: Optional[str] = None,
        migration_guide_url: Optional[str] = None
) -> Callable:
    """
    Create a property that raises an AttributeError when accessed for removed fields.

    This function is used to mark configuration fields that have been removed
    from DataGuild configuration models. When users attempt to access these
    fields, they receive a clear error message explaining the removal.

    Args:
        reason: Explanation of why the field was removed and what to use instead
        removed_in_version: Optional version string when the field was removed
        migration_guide_url: Optional URL to migration documentation

    Returns:
        Property that raises AttributeError when accessed

    Raises:
        AttributeError: Always raised when the property is accessed

    Examples:
        >>> class MyConfig(BaseModel):
        ...     # New field that replaces the old one
        ...     new_field: str = "default_value"
        ...
        ...     # Old field marked as removed
        ...     old_field = pydantic_removed_field(
        ...         "Use 'new_field' instead. The old field was deprecated due to security concerns.",
        ...         removed_in_version="2.0.0",
        ...         migration_guide_url="https://docs.dataguild.com/migration/v2"
        ...     )
        >>>
        >>> config = MyConfig()
        >>> config.new_field  # Works fine
        'default_value'
        >>> config.old_field  # Raises AttributeError
        AttributeError: This field has been removed: Use 'new_field' instead...
    """

    def _removed_field_getter(self) -> Any:
        """Getter that always raises AttributeError for removed fields."""
        error_parts = [f"This field has been removed: {reason}"]

        if removed_in_version:
            error_parts.append(f"Removed in version {removed_in_version}.")

        if migration_guide_url:
            error_parts.append(f"See migration guide: {migration_guide_url}")

        error_message = " ".join(error_parts)

        # Log the access attempt for monitoring purposes
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_info = f"{frame.f_back.f_code.co_filename}:{frame.f_back.f_lineno}"
            logger.warning(f"Attempted access to removed field from {caller_info}: {error_message}")

        raise AttributeError(error_message)

    def _removed_field_setter(self, value: Any) -> None:
        """Setter that always raises AttributeError for removed fields."""
        error_parts = [f"Cannot set removed field: {reason}"]

        if removed_in_version:
            error_parts.append(f"Removed in version {removed_in_version}.")

        if migration_guide_url:
            error_parts.append(f"See migration guide: {migration_guide_url}")

        error_message = " ".join(error_parts)
        raise AttributeError(error_message)

    return property(_removed_field_getter, _removed_field_setter)


def pydantic_removed_field_simple(reason: str) -> Callable:
    """
    Simplified version of pydantic_removed_field for basic use cases.

    This is a convenience function for cases where you only need to provide
    a simple reason message without version information or migration guides.

    Args:
        reason: Simple explanation of the field removal

    Returns:
        Property that raises AttributeError when accessed

    Examples:
        >>> class MyConfig(BaseModel):
        ...     deprecated_field = pydantic_removed_field_simple("Use new_config_option instead")
    """
    return pydantic_removed_field(reason)


def create_removed_field_warning(
        field_name: str,
        reason: str,
        removed_in_version: Optional[str] = None
) -> str:
    """
    Create a standardized warning message for removed fields.

    This utility function helps create consistent warning messages
    for removed fields across different parts of the DataGuild codebase.

    Args:
        field_name: Name of the removed field
        reason: Reason for removal and migration instructions
        removed_in_version: Optional version when field was removed

    Returns:
        Formatted warning message

    Examples:
        >>> warning = create_removed_field_warning(
        ...     "old_password_field",
        ...     "Use 'secure_password' field instead",
        ...     "2.1.0"
        ... )
        >>> print(warning)
        Field 'old_password_field' has been removed in version 2.1.0: Use 'secure_password' field instead
    """
    if removed_in_version:
        return f"Field '{field_name}' has been removed in version {removed_in_version}: {reason}"
    else:
        return f"Field '{field_name}' has been removed: {reason}"


def validate_no_removed_fields(config_dict: dict, removed_fields: dict) -> None:
    """
    Validate that a configuration dictionary doesn't contain removed fields.

    This function can be used during configuration loading to check for
    the presence of removed fields and provide helpful error messages.

    Args:
        config_dict: Configuration dictionary to validate
        removed_fields: Dictionary mapping removed field names to removal reasons

    Raises:
        ValueError: If any removed fields are found in the configuration

    Examples:
        >>> removed_fields = {
        ...     "old_field": "Use new_field instead",
        ...     "deprecated_option": "This option is no longer supported"
        ... }
        >>> config = {"new_field": "value", "old_field": "should_error"}
        >>> validate_no_removed_fields(config, removed_fields)
        ValueError: Configuration contains removed fields: old_field (Use new_field instead)
    """
    found_removed = []

    for field_name in config_dict:
        if field_name in removed_fields:
            reason = removed_fields[field_name]
            found_removed.append(f"{field_name} ({reason})")

    if found_removed:
        error_message = f"Configuration contains removed fields: {', '.join(found_removed)}"
        raise ValueError(error_message)


class RemovedFieldDescriptor:
    """
    Descriptor class for more advanced removed field handling.

    This descriptor provides more control over removed field behavior,
    including the ability to customize error messages based on context.
    """

    def __init__(
            self,
            reason: str,
            removed_in_version: Optional[str] = None,
            migration_guide_url: Optional[str] = None,
            custom_error_class: type = AttributeError
    ):
        """
        Initialize the removed field descriptor.

        Args:
            reason: Explanation of the field removal
            removed_in_version: Optional version when field was removed
            migration_guide_url: Optional URL to migration documentation
            custom_error_class: Custom exception class to raise (default: AttributeError)
        """
        self.reason = reason
        self.removed_in_version = removed_in_version
        self.migration_guide_url = migration_guide_url
        self.custom_error_class = custom_error_class

    def __get__(self, obj, objtype=None):
        """Handle field access."""
        if obj is None:
            return self

        error_parts = [f"This field has been removed: {self.reason}"]

        if self.removed_in_version:
            error_parts.append(f"Removed in version {self.removed_in_version}.")

        if self.migration_guide_url:
            error_parts.append(f"See migration guide: {self.migration_guide_url}")

        error_message = " ".join(error_parts)
        raise self.custom_error_class(error_message)

    def __set__(self, obj, value):
        """Handle field assignment."""
        error_message = f"Cannot set removed field: {self.reason}"
        raise self.custom_error_class(error_message)

    def __delete__(self, obj):
        """Handle field deletion."""
        error_message = f"Cannot delete removed field: {self.reason}"
        raise self.custom_error_class(error_message)


# Export all functions and classes
__all__ = [
    'pydantic_removed_field',
    'pydantic_removed_field_simple',
    'create_removed_field_warning',
    'validate_no_removed_fields',
    'RemovedFieldDescriptor',
]

# Example usage and testing (for development purposes)
if __name__ == "__main__":
    from pydantic import BaseModel

    print("=== DataGuild Field Removal Validation Examples ===\n")


    # Example 1: Basic removed field
    class ExampleConfig(BaseModel):
        current_field: str = "active_field"

        removed_field = pydantic_removed_field(
            "Use 'current_field' instead. This field was removed for security reasons.",
            removed_in_version="2.0.0",
            migration_guide_url="https://docs.dataguild.com/migration/v2"
        )

        simple_removed = pydantic_removed_field_simple("No longer supported")


    print("Example 1: Testing removed field access")
    config = ExampleConfig()
    print(f"Current field value: {config.current_field}")

    try:
        print(f"Removed field value: {config.removed_field}")
    except AttributeError as e:
        print(f"Expected error: {e}")

    try:
        config.removed_field = "new_value"
    except AttributeError as e:
        print(f"Expected error on assignment: {e}")

    print()

    # Example 2: Configuration validation
    print("Example 2: Configuration validation")
    removed_fields = {
        "old_password": "Use 'secure_password' instead",
        "deprecated_timeout": "Use 'connection_timeout' instead"
    }

    valid_config = {"current_field": "value", "secure_password": "secret"}
    invalid_config = {"current_field": "value", "old_password": "should_error"}

    try:
        validate_no_removed_fields(valid_config, removed_fields)
        print("Valid configuration passed validation")
    except ValueError as e:
        print(f"Unexpected error: {e}")

    try:
        validate_no_removed_fields(invalid_config, removed_fields)
        print("This should not print")
    except ValueError as e:
        print(f"Expected validation error: {e}")

    print()

    # Example 3: Warning message generation
    print("Example 3: Warning message generation")
    warning = create_removed_field_warning(
        "legacy_option",
        "Use 'new_option' for better performance",
        "1.5.0"
    )
    print(f"Generated warning: {warning}")
