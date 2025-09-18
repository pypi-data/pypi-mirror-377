"""
Common configuration utilities and base classes for DataGuild.

This module provides foundational configuration classes, validation utilities,
and common patterns used across all DataGuild components.
"""

import re
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Pattern, Type, Union, Set
from pydantic import BaseModel, Field, validator, PrivateAttr
from pydantic.error_wrappers import ValidationError

logger = logging.getLogger(__name__)


class MetaError(Exception):
    """General exception class for metadata processing errors."""

    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        if self.code:
            return f"MetaError(code={self.code}): {self.message}"
        return f"MetaError: {self.message}"


class ConfigurationError(MetaError):
    """Custom exception for configuration-related errors."""
    pass


class ConfigModel(BaseModel):
    """
    Enhanced base configuration model with common functionality.
    """

    class Config:
        """Pydantic configuration for enhanced functionality."""
        arbitrary_types_allowed = True
        validate_assignment = True
        extra = "forbid"
        use_enum_values = True
        validate_all = True

    def dict_with_defaults(self) -> Dict[str, Any]:
        """Get dictionary representation including default values."""
        return self.dict(exclude_unset=False, exclude_none=False)

    def update_with_dict(self, updates: Dict[str, Any]) -> "ConfigModel":
        """Create new instance with updated values from dictionary."""
        current_dict = self.dict()
        current_dict.update(updates)
        return self.__class__(**current_dict)

    def validate_required_fields(self, required_fields: List[str]) -> None:
        """Validate that required fields are present and not None."""
        missing_fields = []
        for field in required_fields:
            value = getattr(self, field, None)
            if value is None:
                missing_fields.append(field)

        if missing_fields:
            raise ConfigurationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )


class AllowDenyPattern(BaseModel):
    """
    Enhanced pattern matching for allow/deny filtering with comprehensive functionality.

    ✅ FIXED: Uses PrivateAttr for compiled patterns to work with Pydantic
    """

    allow: List[str] = Field(
        default_factory=lambda: [".*"],
        description="List of regex patterns to allow. Default allows everything."
    )

    deny: List[str] = Field(
        default_factory=list,
        description="List of regex patterns to deny. Takes precedence over allow patterns."
    )

    ignoreCase: bool = Field(
        default=False,
        description="Whether to ignore case when matching patterns."
    )

    # ✅ CRITICAL FIX: Use PrivateAttr for compiled patterns
    _compiled_allow: Optional[List[Pattern]] = PrivateAttr(default=None)
    _compiled_deny: Optional[List[Pattern]] = PrivateAttr(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for better performance."""
        flags = re.IGNORECASE if self.ignoreCase else 0

        try:
            # ✅ Now this works because _compiled_allow is PrivateAttr
            self._compiled_allow = [re.compile(pattern, flags) for pattern in self.allow]
            self._compiled_deny = [re.compile(pattern, flags) for pattern in self.deny]
        except re.error as e:
            raise ConfigurationError(f"Invalid regex pattern: {e}")

    def allowed(self, value: str) -> bool:
        """
        Check if a value is allowed by the pattern configuration.

        Args:
            value: String value to check against patterns

        Returns:
            True if value is allowed, False otherwise
        """
        if not isinstance(value, str):
            value = str(value)

        # Check deny patterns first (they take precedence)
        if self._compiled_deny:
            for pattern in self._compiled_deny:
                if pattern.search(value):
                    return False

        # Check allow patterns
        if self._compiled_allow:
            for pattern in self._compiled_allow:
                if pattern.search(value):
                    return True

        return False

    def filter_list(self, values: List[str]) -> List[str]:
        """Filter a list of values using the allow/deny patterns."""
        return [value for value in values if self.allowed(value)]

    def get_allowed_count(self, values: List[str]) -> int:
        """Get count of allowed values from a list."""
        return len(self.filter_list(values))

    @classmethod
    def allow_all(cls) -> "AllowDenyPattern":
        """Create pattern that allows everything."""
        return cls(allow=[".*"], deny=[])

    @classmethod
    def deny_all(cls) -> "AllowDenyPattern":
        """Create pattern that denies everything."""
        return cls(allow=[], deny=[".*"])

    @classmethod
    def from_lists(
            cls,
            allow: Optional[List[str]] = None,
            deny: Optional[List[str]] = None,
            ignore_case: bool = False
    ) -> "AllowDenyPattern":
        """Create pattern from allow and deny lists."""
        return cls(
            allow=allow or [".*"],
            deny=deny or [],
            ignoreCase=ignore_case
        )


class DynamicTypedConfig(ConfigModel):
    """
    Configuration class supporting dynamic typing based on 'type' field.
    """

    type: str = Field(description="Type identifier for dynamic configuration")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific configuration parameters"
    )

    @validator("type")
    def validate_type_format(cls, v):
        """Validate type follows expected format."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Type must be a non-empty string")
        return v.strip()

    def get_typed_config(self, target_class: Type[ConfigModel]) -> ConfigModel:
        """Parse config dict as specific configuration class."""
        try:
            return target_class.parse_obj(self.config)
        except ValidationError as e:
            raise ConfigurationError(f"Invalid configuration for type '{self.type}': {e}")


def validate_config(
        config: Dict[str, Any],
        config_class: Type[ConfigModel]
) -> ConfigModel:
    """Validate configuration dictionary against configuration class."""
    try:
        return config_class.parse_obj(config)
    except ValidationError as e:
        error_details = []
        for error in e.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            error_details.append(f"{field_path}: {error['msg']}")

        raise ConfigurationError(
            f"Configuration validation failed:\n" + "\n".join(error_details)
        )


def merge_configs(
        base_config: Dict[str, Any],
        override_config: Dict[str, Any],
        deep_merge: bool = True
) -> Dict[str, Any]:
    """Merge two configuration dictionaries with optional deep merging."""
    if not deep_merge:
        merged = base_config.copy()
        merged.update(override_config)
        return merged

    def _deep_merge(base: Dict, override: Dict) -> Dict:
        """Recursively merge nested dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
            ):
                result[key] = _deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    return _deep_merge(base_config, override_config)


class EnvironmentVariableConfig(ConfigModel):
    """Configuration for environment variable substitution."""

    prefix: str = Field(
        default="DATAGUILD_",
        description="Prefix for environment variables"
    )

    required_vars: Set[str] = Field(
        default_factory=set,
        description="Set of required environment variable names"
    )

    default_values: Dict[str, str] = Field(
        default_factory=dict,
        description="Default values for environment variables"
    )

    def get_env_var(self, name: str) -> Optional[str]:
        """Get environment variable value with prefix and default handling."""
        import os

        # Try with prefix first
        prefixed_name = f"{self.prefix}{name}"
        value = os.getenv(prefixed_name)

        if value is None:
            # Try without prefix
            value = os.getenv(name)

        if value is None and name in self.default_values:
            # Use default value
            value = self.default_values[name]

        return value

    def validate_required_env_vars(self) -> None:
        """Validate that all required environment variables are present."""
        missing_vars = []

        for var_name in self.required_vars:
            if self.get_env_var(var_name) is None:
                missing_vars.append(f"{self.prefix}{var_name}")

        if missing_vars:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )


# Additional common classes for metadata support
class StringMap(BaseModel):
    """A simple string-to-string mapping."""

    properties: Dict[str, str] = Field(default_factory=dict)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.properties.get(key, default)

    def set(self, key: str, value: str) -> None:
        self.properties[key] = value


class AuditStamp(BaseModel):
    """Audit information for tracking changes."""

    time: int = Field(description="Timestamp in milliseconds")
    actor: str = Field(description="Actor who made the change")
    impersonator: Optional[str] = Field(default=None)

    @classmethod
    def create_now(cls, actor: str, impersonator: Optional[str] = None) -> "AuditStamp":
        """Create audit stamp with current timestamp."""
        import time
        return cls(
            time=int(time.time() * 1000),
            actor=actor,
            impersonator=impersonator
        )


class GlobalTags(BaseModel):
    """Global tags applied to entities."""

    tags: List[Dict[str, Any]] = Field(default_factory=list)

    def add_tag(self, tag_urn: str) -> None:
        tag_ref = {"tag": tag_urn}
        if tag_ref not in self.tags:
            self.tags.append(tag_ref)


class GlossaryTerms(BaseModel):
    """Glossary terms applied to entities."""

    terms: List[Dict[str, Any]] = Field(default_factory=list)

    def add_term(self, term_urn: str) -> None:
        term_ref = {"urn": term_urn}
        if term_ref not in self.terms:
            self.terms.append(term_ref)


class DatasetLineageType(str, Enum):
    """Types of dataset lineage relationships."""
    COPY = "COPY"
    TRANSFORMED = "TRANSFORMED"
    VIEW = "VIEW"


# Global configuration registry
_CONFIG_REGISTRY: Dict[str, Type[ConfigModel]] = {}


def register_config_class(type_name: str, config_class: Type[ConfigModel]) -> None:
    """Register a configuration class for dynamic type resolution."""
    _CONFIG_REGISTRY[type_name] = config_class
    logger.debug(f"Registered configuration class: {type_name} -> {config_class}")


def get_config_class(type_name: str) -> Optional[Type[ConfigModel]]:
    """Get registered configuration class by type name."""
    return _CONFIG_REGISTRY.get(type_name)


def list_registered_config_types() -> List[str]:
    """Get list of all registered configuration type names."""
    return list(_CONFIG_REGISTRY.keys())


# Export all classes and functions
__all__ = [
    'MetaError',
    'ConfigurationError',
    'ConfigModel',
    'AllowDenyPattern',
    'DynamicTypedConfig',
    'EnvironmentVariableConfig',
    'StringMap',
    'AuditStamp',
    'GlobalTags',
    'GlossaryTerms',
    'DatasetLineageType',
    'validate_config',
    'merge_configs',
    'register_config_class',
    'get_config_class',
    'list_registered_config_types',
]
