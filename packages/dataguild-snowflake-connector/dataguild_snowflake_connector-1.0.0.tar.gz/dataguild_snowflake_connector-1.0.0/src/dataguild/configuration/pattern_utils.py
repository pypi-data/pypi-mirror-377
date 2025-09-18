"""
Pattern utilities and regex helpers for DataGuild configuration validation.

This module provides commonly used regex patterns and validation functions
for various data formats and identifiers used throughout DataGuild, including
schema filtering and platform-specific validation capabilities.
"""

import re
import logging
from typing import List, Pattern, Optional, Union, Set, Dict
from enum import Enum

logger = logging.getLogger(__name__)

# Common regex patterns used throughout DataGuild
UUID_REGEX = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
SNOWFLAKE_IDENTIFIER_REGEX = r"^[A-Za-z_][A-Za-z0-9_$]*$"
DATABASE_NAME_REGEX = r"^[A-Za-z][A-Za-z0-9_-]*$"
SCHEMA_NAME_REGEX = r"^[A-Za-z_][A-Za-z0-9_$]*$"
TABLE_NAME_REGEX = r"^[A-Za-z_][A-Za-z0-9_$]*$"
URN_REGEX = r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$"

# Platform-specific patterns
AWS_ACCOUNT_ID_REGEX = r"^\d{12}$"
GCP_PROJECT_ID_REGEX = r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$"
AZURE_SUBSCRIPTION_ID_REGEX = UUID_REGEX

# URL patterns
HTTP_URL_REGEX = r"^https?://(?:[-\w.])+(?::[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.]*))?(?:#(?:[\w.]*))?)?$"
JDBC_URL_REGEX = r"^jdbc:[a-zA-Z0-9]+://.*$"

# Compiled patterns for performance
_COMPILED_PATTERNS = {}


class DataPlatform(str, Enum):
    """Supported data platforms for schema validation."""
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    DATABRICKS = "databricks"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class SchemaAllowancePolicy(str, Enum):
    """Policies for schema allowance validation."""
    STRICT = "strict"          # Only explicitly allowed schemas
    PERMISSIVE = "permissive"  # All schemas except explicitly denied
    CUSTOM = "custom"          # Custom validation logic


# ✅ ADDED: Platform-specific allowed schemas configuration
PLATFORM_ALLOWED_SCHEMAS: Dict[str, Set[str]] = {
    DataPlatform.SNOWFLAKE: {
        'information_schema',
        'public',
        'account_usage',
        'reader_account_usage',
        'snowflake',
        'util_db'
    },
    DataPlatform.BIGQUERY: {
        'information_schema',
        'public',
        'dataset',
        '__sessions__'
    },
    DataPlatform.REDSHIFT: {
        'information_schema',
        'public',
        'pg_catalog',
        'sys'
    },
    DataPlatform.DATABRICKS: {
        'information_schema',
        'default',
        'hive_metastore'
    },
    DataPlatform.POSTGRES: {
        'information_schema',
        'public',
        'pg_catalog',
        'pg_toast'
    },
    DataPlatform.MYSQL: {
        'information_schema',
        'mysql',
        'performance_schema',
        'sys'
    }
}

# ✅ ADDED: Platform-specific denied schemas (system/internal schemas to skip)
PLATFORM_DENIED_SCHEMAS: Dict[str, Set[str]] = {
    DataPlatform.SNOWFLAKE: {
        'snowflake_sample_data',
        'util_db',
        'reader_account_usage'
    },
    DataPlatform.BIGQUERY: {
        'sys',
        '__backup__',
        '__restored_dataset__'
    },
    DataPlatform.REDSHIFT: {
        'pg_internal',
        'padb_harvest'
    },
    DataPlatform.POSTGRES: {
        'pg_temp',
        'pg_toast_temp'
    }
}


class SchemaValidator:
    """
    ✅ ADDED: Advanced schema validation with platform-specific rules.

    Provides flexible schema filtering capabilities with support for:
    - Platform-specific allowed/denied lists
    - Custom validation patterns
    - Configurable allowance policies
    """

    def __init__(
        self,
        platform: str,
        policy: SchemaAllowancePolicy = SchemaAllowancePolicy.STRICT,
        custom_allowed: Optional[Set[str]] = None,
        custom_denied: Optional[Set[str]] = None,
        case_sensitive: bool = False
    ):
        """
        Initialize schema validator.

        Args:
            platform: Data platform name
            policy: Allowance policy to use
            custom_allowed: Additional allowed schemas
            custom_denied: Additional denied schemas
            case_sensitive: Whether schema names are case sensitive
        """
        self.platform = platform.lower() if platform else ""
        self.policy = policy
        self.case_sensitive = case_sensitive

        # Build allowed and denied sets
        self._build_schema_sets(custom_allowed, custom_denied)

    def _build_schema_sets(
        self,
        custom_allowed: Optional[Set[str]],
        custom_denied: Optional[Set[str]]
    ) -> None:
        """Build the allowed and denied schema sets based on platform and policy."""
        # Get platform defaults
        platform_allowed = PLATFORM_ALLOWED_SCHEMAS.get(self.platform, set())
        platform_denied = PLATFORM_DENIED_SCHEMAS.get(self.platform, set())

        # Normalize case if needed
        if not self.case_sensitive:
            platform_allowed = {s.lower() for s in platform_allowed}
            platform_denied = {s.lower() for s in platform_denied}

            if custom_allowed:
                custom_allowed = {s.lower() for s in custom_allowed}
            if custom_denied:
                custom_denied = {s.lower() for s in custom_denied}

        # Build final sets based on policy
        if self.policy == SchemaAllowancePolicy.STRICT:
            self.allowed_schemas = platform_allowed.copy()
            if custom_allowed:
                self.allowed_schemas.update(custom_allowed)
        else:
            self.allowed_schemas = set()  # Not used in permissive mode

        self.denied_schemas = platform_denied.copy()
        if custom_denied:
            self.denied_schemas.update(custom_denied)

    def is_schema_allowed(self, schema_name: str) -> bool:
        """
        Check if schema is allowed based on configured policy.

        Args:
            schema_name: Schema name to validate

        Returns:
            True if schema is allowed, False otherwise
        """
        if not schema_name or not isinstance(schema_name, str):
            return False

        # Normalize case if needed
        normalized_name = schema_name.lower() if not self.case_sensitive else schema_name

        # Check denied list first (always applies)
        if normalized_name in self.denied_schemas:
            return False

        # Apply policy-specific logic
        if self.policy == SchemaAllowancePolicy.STRICT:
            return normalized_name in self.allowed_schemas
        elif self.policy == SchemaAllowancePolicy.PERMISSIVE:
            return True  # Allow everything not in denied list
        else:  # CUSTOM policy
            return self._custom_validation(normalized_name)

    def _custom_validation(self, schema_name: str) -> bool:
        """Override this method for custom validation logic."""
        # Default custom validation - can be overridden
        return True

    def get_allowed_schemas(self) -> Set[str]:
        """Get set of explicitly allowed schemas."""
        return self.allowed_schemas.copy()

    def get_denied_schemas(self) -> Set[str]:
        """Get set of explicitly denied schemas."""
        return self.denied_schemas.copy()

    def add_allowed_schema(self, schema_name: str) -> None:
        """Add schema to allowed list."""
        normalized_name = schema_name.lower() if not self.case_sensitive else schema_name
        self.allowed_schemas.add(normalized_name)

    def add_denied_schema(self, schema_name: str) -> None:
        """Add schema to denied list."""
        normalized_name = schema_name.lower() if not self.case_sensitive else schema_name
        self.denied_schemas.add(normalized_name)

    def remove_allowed_schema(self, schema_name: str) -> None:
        """Remove schema from allowed list."""
        normalized_name = schema_name.lower() if not self.case_sensitive else schema_name
        self.allowed_schemas.discard(normalized_name)

    def remove_denied_schema(self, schema_name: str) -> None:
        """Remove schema from denied list."""
        normalized_name = schema_name.lower() if not self.case_sensitive else schema_name
        self.denied_schemas.discard(normalized_name)


def is_schema_allowed(
    schema_pattern: 'AllowDenyPattern',
    schema_name: str,
    db_name: str,
    match_fully_qualified_names: bool = False
) -> bool:
    """
    Check if a schema should be included based on filter patterns.
    
    Args:
        schema_pattern: AllowDenyPattern configuration for schema filtering
        schema_name: Name of the schema to check
        db_name: Name of the database
        match_fully_qualified_names: Whether to match against fully qualified name
    
    Returns:
        True if schema is allowed, False otherwise
    """
    try:
        if match_fully_qualified_names:
            # Match against fully qualified name "database.schema"
            qualified_name = f"{db_name}.{schema_name}"
            return schema_pattern.allowed(qualified_name)
        else:
            # Match against schema name only
            return schema_pattern.allowed(schema_name)
    except Exception as e:
        logger.error(f"Error checking schema allowance for {db_name}.{schema_name}: {e}")
        return False


# ✅ ADDED: Convenience function for simple schema validation
def is_schema_allowed_simple(
    schema_name: str,
    platform: str,
    policy: SchemaAllowancePolicy = SchemaAllowancePolicy.STRICT,
    custom_allowed: Optional[Set[str]] = None,
    custom_denied: Optional[Set[str]] = None
) -> bool:
    """
    Simple function to check if a schema is allowed for a given platform.

    Args:
        schema_name: Name of the schema to validate
        platform: Data platform (snowflake, bigquery, etc.)
        policy: Allowance policy to use
        custom_allowed: Additional schemas to allow
        custom_denied: Additional schemas to deny

    Returns:
        True if schema is allowed, False otherwise

    Examples:
        >>> is_schema_allowed('public', 'snowflake')
        True
        >>> is_schema_allowed('information_schema', 'bigquery')
        True
        >>> is_schema_allowed('my_custom_schema', 'snowflake',
        ...                   policy=SchemaAllowancePolicy.PERMISSIVE)
        True
    """
    validator = SchemaValidator(
        platform=platform,
        policy=policy,
        custom_allowed=custom_allowed,
        custom_denied=custom_denied
    )
    return validator.is_schema_allowed(schema_name)


def get_compiled_pattern(pattern: str, flags: int = 0) -> Pattern:
    """
    Get compiled regex pattern with caching for performance.

    Args:
        pattern: Regex pattern string
        flags: Regex flags (e.g., re.IGNORECASE)

    Returns:
        Compiled regex pattern

    Raises:
        re.error: If pattern is invalid
    """
    cache_key = (pattern, flags)
    if cache_key not in _COMPILED_PATTERNS:
        try:
            _COMPILED_PATTERNS[cache_key] = re.compile(pattern, flags)
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
            raise
    return _COMPILED_PATTERNS[cache_key]


def validate_uuid(value: str) -> bool:
    """
    Validate if string is a valid UUID format.

    Args:
        value: String to validate

    Returns:
        True if valid UUID format, False otherwise
    """
    if not isinstance(value, str):
        return False
    pattern = get_compiled_pattern(UUID_REGEX)
    return bool(pattern.fullmatch(value))


def validate_email(value: str) -> bool:
    """
    Validate if string is a valid email format.

    Args:
        value: String to validate

    Returns:
        True if valid email format, False otherwise
    """
    if not isinstance(value, str):
        return False
    pattern = get_compiled_pattern(EMAIL_REGEX)
    return bool(pattern.fullmatch(value))


def validate_snowflake_identifier(value: str) -> bool:
    """
    Validate if string is a valid Snowflake identifier.

    Args:
        value: String to validate

    Returns:
        True if valid Snowflake identifier, False otherwise
    """
    if not isinstance(value, str):
        return False
    # Check basic pattern
    pattern = get_compiled_pattern(SNOWFLAKE_IDENTIFIER_REGEX)
    if not pattern.fullmatch(value):
        return False
    # Check length constraints (Snowflake identifiers max 255 chars)
    if len(value) > 255:
        return False
    # Check for reserved words (simplified list)
    reserved_words = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
        'CREATE', 'DROP', 'ALTER', 'TABLE', 'VIEW', 'DATABASE', 'SCHEMA'
    }
    if value.upper() in reserved_words:
        return False
    return True


def validate_database_name(value: str) -> bool:
    """
    Validate if string is a valid database name.

    Args:
        value: String to validate

    Returns:
        True if valid database name, False otherwise
    """
    if not isinstance(value, str):
        return False
    pattern = get_compiled_pattern(DATABASE_NAME_REGEX)
    return bool(pattern.fullmatch(value)) and len(value) <= 128


def validate_schema_name(value: str, platform: str = "generic") -> bool:
    """
    ✅ ENHANCED: Validate if string is a valid schema name with platform-specific rules.

    Args:
        value: String to validate
        platform: Target platform for validation

    Returns:
        True if valid schema name, False otherwise
    """
    if not isinstance(value, str):
        return False

    # Basic pattern validation
    pattern = get_compiled_pattern(SCHEMA_NAME_REGEX)
    if not pattern.fullmatch(value):
        return False

    # Platform-specific validation
    if platform.lower() == "snowflake":
        return validate_snowflake_identifier(value)
    elif platform.lower() == "bigquery":
        # BigQuery dataset names have specific rules
        if len(value) > 1024:
            return False
        # Must contain only letters, numbers, and underscores
        bq_pattern = get_compiled_pattern(r"^[a-zA-Z0-9_]+$")
        return bool(bq_pattern.fullmatch(value))

    # Generic validation
    return len(value) <= 128


def validate_url(value: str, require_https: bool = False) -> bool:
    """
    Validate if string is a valid HTTP/HTTPS URL.

    Args:
        value: String to validate
        require_https: If True, only HTTPS URLs are valid

    Returns:
        True if valid URL, False otherwise
    """
    if not isinstance(value, str):
        return False
    if require_https and not value.startswith('https://'):
        return False
    pattern = get_compiled_pattern(HTTP_URL_REGEX)
    return bool(pattern.fullmatch(value))


def validate_urn(value: str) -> bool:
    """
    Validate if string is a valid URN format.

    Args:
        value: String to validate

    Returns:
        True if valid URN format, False otherwise
    """
    if not isinstance(value, str):
        return False
    pattern = get_compiled_pattern(URN_REGEX)
    return bool(pattern.fullmatch(value))


def compile_pattern_list(
        patterns: List[str],
        flags: int = 0,
        validate_patterns: bool = True
) -> List[Pattern]:
    """
    Compile a list of regex patterns with validation.

    Args:
        patterns: List of regex pattern strings
        flags: Regex flags to apply to all patterns
        validate_patterns: Whether to validate patterns before compiling

    Returns:
        List of compiled regex patterns

    Raises:
        re.error: If any pattern is invalid and validate_patterns=True
    """
    compiled_patterns = []
    for pattern in patterns:
        try:
            compiled_pattern = get_compiled_pattern(pattern, flags)
            compiled_patterns.append(compiled_pattern)
        except re.error as e:
            if validate_patterns:
                raise re.error(f"Invalid pattern '{pattern}': {e}")
            else:
                logger.warning(f"Skipping invalid pattern '{pattern}': {e}")
                continue
    return compiled_patterns


def match_any_pattern(
        value: str,
        patterns: Union[List[str], List[Pattern]],
        flags: int = 0
) -> bool:
    """
    Check if value matches any of the provided patterns.

    Args:
        value: String value to check
        patterns: List of regex patterns (strings or compiled)
        flags: Regex flags if patterns are strings

    Returns:
        True if value matches any pattern, False otherwise
    """
    if not isinstance(value, str):
        value = str(value)
    for pattern in patterns:
        if isinstance(pattern, str):
            compiled_pattern = get_compiled_pattern(pattern, flags)
        elif isinstance(pattern, Pattern):
            compiled_pattern = pattern
        else:
            logger.warning(f"Skipping invalid pattern type: {type(pattern)}")
            continue
        if compiled_pattern.search(value):
            return True
    return False


def extract_identifiers_from_qualified_name(
        qualified_name: str,
        separator: str = ".",
        max_parts: Optional[int] = None
) -> List[str]:
    """
    Extract individual identifiers from qualified name.

    Args:
        qualified_name: Qualified name (e.g., "database.schema.table")
        separator: Separator character (default: ".")
        max_parts: Maximum number of parts to extract

    Returns:
        List of individual identifiers
    """
    if not isinstance(qualified_name, str):
        return []
    parts = qualified_name.split(separator)
    if max_parts is not None:
        parts = parts[:max_parts]
    # Remove empty parts and strip whitespace
    return [part.strip() for part in parts if part.strip()]


def validate_qualified_name(
        qualified_name: str,
        expected_parts: int,
        separator: str = ".",
        identifier_validator: Optional[callable] = None
) -> bool:
    """
    Validate qualified name format and individual identifiers.

    Args:
        qualified_name: Qualified name to validate
        expected_parts: Expected number of parts in the name
        separator: Separator character
        identifier_validator: Function to validate individual identifiers

    Returns:
        True if qualified name is valid, False otherwise
    """
    parts = extract_identifiers_from_qualified_name(qualified_name, separator)
    if len(parts) != expected_parts:
        return False
    if identifier_validator:
        return all(identifier_validator(part) for part in parts)
    return True


def sanitize_identifier(
        identifier: str,
        replacement_char: str = "_",
        max_length: Optional[int] = None
) -> str:
    """
    Sanitize identifier by replacing invalid characters.

    Args:
        identifier: Identifier to sanitize
        replacement_char: Character to use for replacements
        max_length: Maximum length (truncate if longer)

    Returns:
        Sanitized identifier
    """
    if not isinstance(identifier, str):
        identifier = str(identifier)
    # Replace invalid characters with replacement character
    sanitized = re.sub(r'[^A-Za-z0-9_]', replacement_char, identifier)
    # Ensure it starts with letter or underscore
    if sanitized and not re.match(r'^[A-Za-z_]', sanitized):
        sanitized = f"_{sanitized}"
    # Truncate if necessary
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    # Ensure not empty
    if not sanitized:
        sanitized = "unnamed"
    return sanitized


def filter_schemas_by_platform(
    schemas: List[str],
    platform: str,
    policy: SchemaAllowancePolicy = SchemaAllowancePolicy.STRICT,
    custom_allowed: Optional[Set[str]] = None,
    custom_denied: Optional[Set[str]] = None
) -> List[str]:
    """
    ✅ ADDED: Filter list of schemas based on platform-specific rules.

    Args:
        schemas: List of schema names to filter
        platform: Target platform
        policy: Allowance policy
        custom_allowed: Additional allowed schemas
        custom_denied: Additional denied schemas

    Returns:
        Filtered list of schemas
    """
    validator = SchemaValidator(
        platform=platform,
        policy=policy,
        custom_allowed=custom_allowed,
        custom_denied=custom_denied
    )

    return [schema for schema in schemas if validator.is_schema_allowed(schema)]


def get_platform_schema_info(platform: str) -> Dict[str, Set[str]]:
    """
    ✅ ADDED: Get platform-specific schema configuration.

    Args:
        platform: Platform name

    Returns:
        Dictionary with 'allowed' and 'denied' schema sets
    """
    platform_key = platform.lower()

    return {
        'allowed': PLATFORM_ALLOWED_SCHEMAS.get(platform_key, set()).copy(),
        'denied': PLATFORM_DENIED_SCHEMAS.get(platform_key, set()).copy()
    }


def clear_pattern_cache() -> None:
    """Clear compiled pattern cache to free memory."""
    global _COMPILED_PATTERNS
    _COMPILED_PATTERNS.clear()
    logger.debug("Cleared regex pattern cache")


def get_pattern_cache_size() -> int:
    """Get current size of pattern cache."""
    return len(_COMPILED_PATTERNS)


# Export all functions and classes
__all__ = [
    # Enums
    'DataPlatform',
    'SchemaAllowancePolicy',

    # Main classes
    'SchemaValidator',

    # Schema validation functions
    'is_schema_allowed',
    'filter_schemas_by_platform',
    'get_platform_schema_info',

    # Pattern validation functions
    'validate_uuid',
    'validate_email',
    'validate_snowflake_identifier',
    'validate_database_name',
    'validate_schema_name',
    'validate_url',
    'validate_urn',
    'validate_qualified_name',

    # Pattern utilities
    'get_compiled_pattern',
    'compile_pattern_list',
    'match_any_pattern',
    'extract_identifiers_from_qualified_name',
    'sanitize_identifier',

    # Cache management
    'clear_pattern_cache',
    'get_pattern_cache_size',

    # Constants
    'PLATFORM_ALLOWED_SCHEMAS',
    'PLATFORM_DENIED_SCHEMAS',
]
