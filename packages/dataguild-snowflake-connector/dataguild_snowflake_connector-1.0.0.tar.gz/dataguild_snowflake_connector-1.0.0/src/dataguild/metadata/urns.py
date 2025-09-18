"""
DataGuild Metadata URN Classes

Clean and simple implementations of Universal Resource Name (URN) classes
for DataGuild's metadata system. These provide standardized, type-safe
identifiers for different types of metadata entities.

Author: DataGuild Engineering Team
"""

from typing import Optional
import re


class CorpUserUrn:
    """URN for corporate user entities representing people in the organization."""
    ENTITY_TYPE = "corpuser"

    def __init__(self, username: str):
        """
        Initialize a corporate user URN.

        Args:
            username: Username or email address of the corporate user

        Raises:
            ValueError: If username is empty or invalid
        """
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")

        # Basic validation for username format
        if not re.match(r'^[a-zA-Z0-9._@-]+$', username):
            raise ValueError(f"Invalid username format: {username}")

        self.username = username.strip()

    def urn(self) -> str:
        """Generate the full URN string."""
        return f"urn:li:{self.ENTITY_TYPE}:{self.username}"

    @staticmethod
    def entity_type_urn() -> str:
        """Get the entity type URN for corporate users."""
        return f"urn:li:entityType:{CorpUserUrn.ENTITY_TYPE}"

    @classmethod
    def from_string(cls, urn_string: str) -> 'CorpUserUrn':
        """
        Create a CorpUserUrn from a URN string.

        Args:
            urn_string: URN string to parse

        Returns:
            CorpUserUrn instance

        Raises:
            ValueError: If URN string is invalid
        """
        prefix = f"urn:li:{cls.ENTITY_TYPE}:"
        if not urn_string.startswith(prefix):
            raise ValueError(f"Invalid CorpUserUrn format: {urn_string}")

        username = urn_string[len(prefix):]
        if not username:
            raise ValueError("Username cannot be empty in URN")

        return cls(username)

    @classmethod
    def from_email(cls, email: str) -> 'CorpUserUrn':
        """
        Create a CorpUserUrn from an email address.

        Args:
            email: Email address

        Returns:
            CorpUserUrn instance using email as username
        """
        # Basic email validation
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError(f"Invalid email format: {email}")

        return cls(email)

    def get_display_name(self) -> str:
        """
        Get a human-readable display name from the username.

        Returns:
            Formatted display name
        """
        # If it's an email, use the part before @
        if '@' in self.username:
            display_name = self.username.split('@')[0]
        else:
            display_name = self.username

        # Replace common separators with spaces and title case
        display_name = display_name.replace('_', ' ').replace('.', ' ').replace('-', ' ')
        return display_name.title()

    def get_domain(self) -> Optional[str]:
        """
        Get the domain from username if it's an email address.

        Returns:
            Domain name or None if not an email
        """
        if '@' in self.username:
            return self.username.split('@')[1]
        return None

    def is_email(self) -> bool:
        """Check if the username is an email address."""
        return '@' in self.username

    def __str__(self) -> str:
        """String representation returns the URN."""
        return self.urn()

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"CorpUserUrn(username='{self.username}')"

    def __eq__(self, other) -> bool:
        """Check equality with another CorpUserUrn."""
        if not isinstance(other, CorpUserUrn):
            return False
        return self.username.lower() == other.username.lower()

    def __hash__(self) -> int:
        """Hash for using as dictionary key."""
        return hash(self.username.lower())


class ContainerUrn:
    """URN for container entities like databases, schemas, and folders."""
    ENTITY_TYPE = "container"

    def __init__(self, container_id: str):
        if not container_id or not isinstance(container_id, str):
            raise ValueError("Container ID must be a non-empty string")
        self.container_id = container_id

    def urn(self) -> str:
        """Generate the full URN string."""
        return f"urn:li:container:{self.container_id}"

    @staticmethod
    def entity_type_urn() -> str:
        """Get the entity type URN for containers."""
        return f"urn:li:entityType:{ContainerUrn.ENTITY_TYPE}"

    @classmethod
    def from_string(cls, urn_string: str) -> 'ContainerUrn':
        """Create ContainerUrn from URN string."""
        prefix = "urn:li:container:"
        if not urn_string.startswith(prefix):
            raise ValueError(f"Invalid ContainerUrn format: {urn_string}")
        container_id = urn_string[len(prefix):]
        return cls(container_id)

    def __str__(self) -> str:
        return self.urn()

    def __repr__(self) -> str:
        return f"ContainerUrn(container_id='{self.container_id}')"


class DatasetUrn:
    """URN for dataset entities like tables, views, and streams."""
    ENTITY_TYPE = "dataset"

    def __init__(self, platform: str, dataset_name: str, env: str = "PROD"):
        if not all([platform, dataset_name, env]):
            raise ValueError("Platform, dataset_name, and env must be non-empty strings")
        self.platform = platform
        self.dataset_name = dataset_name
        self.env = env.upper()

    def urn(self) -> str:
        """Generate the full URN string."""
        return f"urn:li:dataset:(urn:li:dataPlatform:{self.platform},{self.dataset_name},{self.env})"

    @staticmethod
    def entity_type_urn() -> str:
        """Get the entity type URN for datasets."""
        return f"urn:li:entityType:{DatasetUrn.ENTITY_TYPE}"

    @classmethod
    def from_string(cls, urn_string: str) -> 'DatasetUrn':
        """Create DatasetUrn from URN string."""
        pattern = r'^urn:li:dataset:\(urn:li:dataPlatform:([^,]+),([^,]+),([^)]+)\)$'
        match = re.match(pattern, urn_string)
        if not match:
            raise ValueError(f"Invalid DatasetUrn format: {urn_string}")

        platform, dataset_name, env = match.groups()
        return cls(platform, dataset_name, env)

    def get_platform_name(self) -> str:
        """Get the platform name."""
        return self.platform

    def get_table_parts(self) -> list:
        """Split dataset name into parts (database.schema.table)."""
        return self.dataset_name.split('.')

    def __str__(self) -> str:
        return self.urn()

    def __repr__(self) -> str:
        return f"DatasetUrn(platform='{self.platform}', dataset_name='{self.dataset_name}', env='{self.env}')"


class DataTypeUrn:
    """URN for data types used in structured properties."""

    # Common data types
    STRING = "urn:li:dataType:string"
    NUMBER = "urn:li:dataType:number"
    BOOLEAN = "urn:li:dataType:boolean"
    DATE = "urn:li:dataType:date"
    URN = "urn:li:dataType:urn"

    def __init__(self, data_type: str):
        if not data_type:
            raise ValueError("Data type must be non-empty string")
        self.data_type = data_type

    def urn(self) -> str:
        """Generate the full URN string."""
        if self.data_type.startswith("urn:li:dataType:"):
            return self.data_type
        return f"urn:li:dataType:{self.data_type}"

    @classmethod
    def string_type(cls) -> 'DataTypeUrn':
        """Create a string data type URN."""
        return cls("string")

    @classmethod
    def number_type(cls) -> 'DataTypeUrn':
        """Create a number data type URN."""
        return cls("number")

    @classmethod
    def boolean_type(cls) -> 'DataTypeUrn':
        """Create a boolean data type URN."""
        return cls("boolean")

    def __str__(self) -> str:
        return self.urn()

    def __repr__(self) -> str:
        return f"DataTypeUrn(data_type='{self.data_type}')"


class EntityTypeUrn:
    """URN for different entity types in the metadata model."""

    def __init__(self, entity_type: str):
        if not entity_type:
            raise ValueError("Entity type must be non-empty string")
        # Remove 'datahub.' prefix if present for consistency
        self.entity_type = entity_type.replace("datahub.", "")

    def urn(self) -> str:
        """Generate the full URN string."""
        return f"urn:li:entityType:{self.entity_type}"

    @classmethod
    def from_string(cls, urn_string: str) -> 'EntityTypeUrn':
        """Create EntityTypeUrn from URN string."""
        prefix = "urn:li:entityType:"
        if not urn_string.startswith(prefix):
            raise ValueError(f"Invalid EntityTypeUrn format: {urn_string}")
        entity_type = urn_string[len(prefix):]
        return cls(entity_type)

    def __str__(self) -> str:
        return self.urn()

    def __repr__(self) -> str:
        return f"EntityTypeUrn(entity_type='{self.entity_type}')"


class SchemaFieldUrn:
    """URN for schema field entities like table columns."""
    ENTITY_TYPE = "schemaField"

    def __init__(self, dataset_urn: str, field_path: str):
        if not dataset_urn or not field_path:
            raise ValueError("Dataset URN and field path must be non-empty strings")
        self.dataset_urn = dataset_urn
        self.field_path = field_path

    def urn(self) -> str:
        """Generate the full URN string."""
        return f"urn:li:schemaField:({self.dataset_urn},{self.field_path})"

    @staticmethod
    def entity_type_urn() -> str:
        """Get the entity type URN for schema fields."""
        return f"urn:li:entityType:{SchemaFieldUrn.ENTITY_TYPE}"

    @classmethod
    def from_string(cls, urn_string: str) -> 'SchemaFieldUrn':
        """Create SchemaFieldUrn from URN string."""
        pattern = r'^urn:li:schemaField:\((.+),([^)]+)\)$'
        match = re.match(pattern, urn_string)
        if not match:
            raise ValueError(f"Invalid SchemaFieldUrn format: {urn_string}")

        dataset_urn, field_path = match.groups()
        return cls(dataset_urn, field_path)

    def __str__(self) -> str:
        return self.urn()

    def __repr__(self) -> str:
        return f"SchemaFieldUrn(dataset_urn='{self.dataset_urn}', field_path='{self.field_path}')"


class StructuredPropertyUrn:
    """URN for structured properties that can be attached to entities."""

    def __init__(self, property_name: str):
        if not property_name:
            raise ValueError("Property name must be non-empty string")
        self.property_name = property_name

    def urn(self) -> str:
        """Generate the full URN string."""
        return f"urn:li:structuredProperty:{self.property_name}"

    @classmethod
    def from_string(cls, urn_string: str) -> 'StructuredPropertyUrn':
        """Create StructuredPropertyUrn from URN string."""
        prefix = "urn:li:structuredProperty:"
        if not urn_string.startswith(prefix):
            raise ValueError(f"Invalid StructuredPropertyUrn format: {urn_string}")
        property_name = urn_string[len(prefix):]
        return cls(property_name)

    def __str__(self) -> str:
        return self.urn()

    def __repr__(self) -> str:
        return f"StructuredPropertyUrn(property_name='{self.property_name}')"


# Utility functions for common URN operations

def create_corp_user_urn(username: str) -> CorpUserUrn:
    """Create a corporate user URN from username."""
    return CorpUserUrn(username)


def create_corp_user_from_email(email: str) -> CorpUserUrn:
    """Create a corporate user URN from email address."""
    return CorpUserUrn.from_email(email)


def create_snowflake_dataset_urn(db_name: str, schema_name: str, table_name: str, env: str = "PROD") -> DatasetUrn:
    """Create a dataset URN for Snowflake tables."""
    dataset_name = f"{db_name}.{schema_name}.{table_name}"
    return DatasetUrn("snowflake", dataset_name, env)


def create_snowflake_container_urn(db_name: str, schema_name: Optional[str] = None) -> ContainerUrn:
    """Create a container URN for Snowflake databases or schemas."""
    if schema_name:
        container_id = f"snowflake.{db_name}.{schema_name}"
    else:
        container_id = f"snowflake.{db_name}"
    return ContainerUrn(container_id)


def create_tag_structured_property_urn(tag_name: str) -> StructuredPropertyUrn:
    """Create a structured property URN for Snowflake tags."""
    return StructuredPropertyUrn(f"snowflake.tag.{tag_name}")


def create_schema_field_urn(dataset_urn: DatasetUrn, field_name: str) -> SchemaFieldUrn:
    """Create a schema field URN for a dataset column."""
    return SchemaFieldUrn(dataset_urn.urn(), field_name)


# Enhanced validation helpers

def is_valid_urn(urn_string: str) -> bool:
    """Validate if a string is a properly formatted URN."""
    if not urn_string or not isinstance(urn_string, str):
        return False

    return (
        urn_string.startswith("urn:li:") and
        len(urn_string.split(":")) >= 3 and
        len(urn_string) > 7  # Minimum valid URN length
    )


def extract_urn_type(urn_string: str) -> Optional[str]:
    """Extract the entity type from a URN string."""
    if not is_valid_urn(urn_string):
        return None

    parts = urn_string.split(":")
    return parts[2] if len(parts) > 2 else None


def parse_urn(urn_string: str):
    """
    Parse a URN string and return the appropriate URN object.

    Args:
        urn_string: URN string to parse

    Returns:
        Appropriate URN object instance

    Raises:
        ValueError: If URN format is invalid or unsupported
    """
    if not is_valid_urn(urn_string):
        raise ValueError(f"Invalid URN format: {urn_string}")

    entity_type = extract_urn_type(urn_string)

    try:
        if entity_type == "corpuser":
            return CorpUserUrn.from_string(urn_string)
        elif entity_type == "dataset":
            return DatasetUrn.from_string(urn_string)
        elif entity_type == "container":
            return ContainerUrn.from_string(urn_string)
        elif entity_type == "schemaField":
            return SchemaFieldUrn.from_string(urn_string)
        elif entity_type == "structuredProperty":
            return StructuredPropertyUrn.from_string(urn_string)
        elif entity_type == "entityType":
            return EntityTypeUrn.from_string(urn_string)
        elif entity_type == "dataType":
            # Extract the data type from the URN
            data_type = urn_string.split(":")[-1]
            return DataTypeUrn(data_type)
        else:
            raise ValueError(f"Unsupported URN entity type: {entity_type}")
    except Exception as e:
        raise ValueError(f"Failed to parse URN '{urn_string}': {e}")


def get_urn_components(urn_string: str) -> dict:
    """
    Extract all components from a URN string.

    Args:
        urn_string: URN string to analyze

    Returns:
        Dictionary containing URN components
    """
    if not is_valid_urn(urn_string):
        return {"valid": False, "error": "Invalid URN format"}

    parts = urn_string.split(":")

    components = {
        "valid": True,
        "full_urn": urn_string,
        "scheme": parts[0] if len(parts) > 0 else None,
        "namespace": parts[1] if len(parts) > 1 else None,
        "entity_type": parts[2] if len(parts) > 2 else None,
        "entity_key": ":".join(parts[3:]) if len(parts) > 3 else None
    }

    return components


# Export all classes and utility functions
__all__ = [
    # URN Classes
    'CorpUserUrn',
    'ContainerUrn',
    'DatasetUrn',
    'DataTypeUrn',
    'EntityTypeUrn',
    'SchemaFieldUrn',
    'StructuredPropertyUrn',

    # Utility Functions
    'create_corp_user_urn',
    'create_corp_user_from_email',
    'create_snowflake_dataset_urn',
    'create_snowflake_container_urn',
    'create_tag_structured_property_urn',
    'create_schema_field_urn',

    # Validation and Parsing
    'is_valid_urn',
    'extract_urn_type',
    'parse_urn',
    'get_urn_components',
]
