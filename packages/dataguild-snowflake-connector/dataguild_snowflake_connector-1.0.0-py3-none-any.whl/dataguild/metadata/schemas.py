"""
DataGuild Metadata Schema System

Comprehensive metadata schema classes for DataGuild including event tracking,
data types, schema definitions, constraints, and dataset properties with
structured event types, severity levels, and rich context information.
"""

import json
import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from uuid import uuid4

logger = logging.getLogger(__name__)


class MetadataEventType(Enum):
    """
    Enumeration of metadata event types for comprehensive tracking.

    Covers all aspects of metadata processing including work units,
    batches, entities, lineage, schema changes, and system events.
    """

    # Work unit lifecycle events
    WORK_UNIT_CREATED = "work_unit_created"
    WORK_UNIT_STARTED = "work_unit_started"
    WORK_UNIT_COMPLETED = "work_unit_completed"
    WORK_UNIT_FAILED = "work_unit_failed"
    WORK_UNIT_RETRYING = "work_unit_retrying"
    WORK_UNIT_CANCELLED = "work_unit_cancelled"
    WORK_UNIT_TIMEOUT = "work_unit_timeout"

    # Batch processing events
    BATCH_CREATED = "batch_created"
    BATCH_STARTED = "batch_started"
    BATCH_COMPLETED = "batch_completed"
    BATCH_FAILED = "batch_failed"
    BATCH_TIMEOUT = "batch_timeout"
    BATCH_CANCELLED = "batch_cancelled"

    # Entity lifecycle events
    ENTITY_DISCOVERED = "entity_discovered"
    ENTITY_CREATED = "entity_created"
    ENTITY_UPDATED = "entity_updated"
    ENTITY_DELETED = "entity_deleted"
    ENTITY_RESTORED = "entity_restored"
    ENTITY_DEPRECATED = "entity_deprecated"

    # Lineage and relationships
    LINEAGE_CREATED = "lineage_created"
    LINEAGE_UPDATED = "lineage_updated"
    LINEAGE_DELETED = "lineage_deleted"
    RELATIONSHIP_CREATED = "relationship_created"
    RELATIONSHIP_UPDATED = "relationship_updated"
    RELATIONSHIP_DELETED = "relationship_deleted"

    # Schema and structure events
    SCHEMA_DISCOVERED = "schema_discovered"
    SCHEMA_CHANGED = "schema_changed"
    SCHEMA_DRIFT_DETECTED = "schema_drift_detected"
    SCHEMA_VALIDATED = "schema_validated"
    SCHEMA_MIGRATION = "schema_migration"

    # Data quality and profiling
    DATA_QUALITY_CHECK = "data_quality_check"
    DATA_PROFILING_STARTED = "data_profiling_started"
    DATA_PROFILING_COMPLETED = "data_profiling_completed"
    DATA_PROFILING_FAILED = "data_profiling_failed"
    ANOMALY_DETECTED = "anomaly_detected"

    # Validation events
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    VALIDATION_ERROR = "validation_error"
    VALIDATION_WARNING = "validation_warning"

    # Connection and system events
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_LOST = "connection_lost"
    CONNECTION_RETRY = "connection_retry"
    CONNECTION_TIMEOUT = "connection_timeout"

    # Rate limiting and quotas
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"
    THROTTLING_APPLIED = "throttling_applied"

    # Security and permissions
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHENTICATION_FAILURE = "authentication_failure"

    # Configuration and settings
    CONFIG_LOADED = "config_loaded"
    CONFIG_UPDATED = "config_updated"
    CONFIG_VALIDATION_ERROR = "config_validation_error"

    # Performance and monitoring
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MEMORY_USAGE_HIGH = "memory_usage_high"
    DISK_USAGE_HIGH = "disk_usage_high"

    # Custom and extensible events
    CUSTOM = "custom"
    DEBUG = "debug"

    @classmethod
    def from_string(cls, value: str) -> "MetadataEventType":
        """Create MetadataEventType from string value."""
        if not value:
            return cls.CUSTOM

        try:
            return cls(value.lower())
        except ValueError:
            logger.warning(f"Unknown event type: {value}, defaulting to CUSTOM")
            return cls.CUSTOM


class MetadataEventSeverity(Enum):
    """
    Event severity levels for filtering and alerting.

    Provides standard severity classification for metadata events
    to enable proper monitoring, alerting, and log management.
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    @classmethod
    def from_string(cls, value: str) -> "MetadataEventSeverity":
        """Create MetadataEventSeverity from string value."""
        if not value:
            return cls.INFO

        try:
            return cls(value.lower())
        except ValueError:
            logger.warning(f"Unknown severity level: {value}, defaulting to INFO")
            return cls.INFO

    def is_error_level(self) -> bool:
        """Check if severity is error or critical."""
        return self in {self.ERROR, self.CRITICAL}

    def is_warning_or_above(self) -> bool:
        """Check if severity is warning or above."""
        return self in {self.WARNING, self.ERROR, self.CRITICAL}


# =====================
# DATA TYPE CLASSES
# =====================

@dataclass
class NullType:
    """Represents a NULL data type."""

    def __str__(self) -> str:
        return "NULL"

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "NULL"}


@dataclass
class BooleanType:
    """Represents a boolean data type."""

    def __str__(self) -> str:
        return "BOOLEAN"

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "BOOLEAN"}


@dataclass
class StringType:
    """Represents a string data type with optional length constraint."""
    length: Optional[int] = None

    def __str__(self) -> str:
        if self.length:
            return f"STRING({self.length})"
        return "STRING"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "STRING",
            "length": self.length
        }


@dataclass
class NumberType:
    """Represents a numeric data type with precision and scale."""
    precision: Optional[int] = None
    scale: Optional[int] = None

    def __str__(self) -> str:
        if self.precision and self.scale:
            return f"NUMBER({self.precision},{self.scale})"
        elif self.precision:
            return f"NUMBER({self.precision})"
        return "NUMBER"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "NUMBER",
            "precision": self.precision,
            "scale": self.scale
        }


@dataclass
class DateType:
    """Represents a date data type."""
    format: Optional[str] = None

    def __str__(self) -> str:
        return "DATE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "DATE",
            "format": self.format
        }


@dataclass
class TimeType:
    """Represents a time data type."""
    precision: Optional[int] = None

    def __str__(self) -> str:
        if self.precision:
            return f"TIME({self.precision})"
        return "TIME"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "TIME",
            "precision": self.precision
        }


@dataclass
class TimeStamp:
    """Represents a timestamp data type."""
    precision: Optional[int] = None
    with_timezone: bool = False

    def __str__(self) -> str:
        base = "TIMESTAMP"
        if self.precision:
            base = f"TIMESTAMP({self.precision})"
        if self.with_timezone:
            base += " WITH TIME ZONE"
        return base

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "TIMESTAMP",
            "precision": self.precision,
            "with_timezone": self.with_timezone
        }


@dataclass
class BytesType:
    """Represents a bytes/binary data type."""
    length: Optional[int] = None

    def __str__(self) -> str:
        if self.length:
            return f"BYTES({self.length})"
        return "BYTES"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BYTES",
            "length": self.length
        }


@dataclass
class ArrayType:
    """Represents an array data type."""
    element_type: Any

    def __str__(self) -> str:
        return f"ARRAY<{self.element_type}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ARRAY",
            "element_type": self.element_type.to_dict() if hasattr(self.element_type, 'to_dict') else str(self.element_type)
        }


@dataclass
class RecordType:
    """Represents a record/struct data type."""
    fields: List['SchemaField'] = field(default_factory=list)

    def __str__(self) -> str:
        field_strs = [f"{field.name}: {field.type}" for field in self.fields]
        return f"RECORD<{', '.join(field_strs)}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "RECORD",
            "fields": [field.to_dict() for field in self.fields]
        }

    def add_field(self, field: 'SchemaField') -> None:
        """Add field to record type."""
        self.fields.append(field)

    def get_field(self, name: str) -> Optional['SchemaField']:
        """Get field by name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None


@dataclass
class SubTypes:
    """Represents union/subtype definitions."""
    types: List[Any] = field(default_factory=list)

    def __str__(self) -> str:
        type_strs = [str(t) for t in self.types]
        return f"UNION<{', '.join(type_strs)}>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UNION",
            "types": [t.to_dict() if hasattr(t, 'to_dict') else str(t) for t in self.types]
        }

    def add_type(self, data_type: Any) -> None:
        """Add type to union."""
        self.types.append(data_type)


# =====================
# SCHEMA CLASSES
# =====================

@dataclass
class SchemaFieldDataType:
    """Represents the data type of a schema field."""
    type_name: str
    type_params: Dict[str, Any] = field(default_factory=dict)
    nullable: bool = True

    def __post_init__(self):
        """Validate schema field data type."""
        if not self.type_name:
            raise ValueError("Type name is required")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type_name": self.type_name,
            "type_params": self.type_params,
            "nullable": self.nullable
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaFieldDataType":
        return cls(
            type_name=data["type_name"],
            type_params=data.get("type_params", {}),
            nullable=data.get("nullable", True)
        )


@dataclass
class SchemaField:
    """Represents a field in a schema."""
    name: str
    type: SchemaFieldDataType
    description: Optional[str] = None
    nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    default_value: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    custom_properties: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate schema field."""
        if not self.name:
            raise ValueError("Field name is required")
        if not self.type:
            raise ValueError("Field type is required")

    def add_tag(self, tag: str) -> None:
        """Add tag to field."""
        self.tags.add(tag)

    def remove_tag(self, tag: str) -> bool:
        """Remove tag from field."""
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """Check if field has tag."""
        return tag in self.tags

    def set_property(self, key: str, value: str) -> None:
        """Set custom property."""
        self.custom_properties[key] = value

    def get_property(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get custom property."""
        return self.custom_properties.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.to_dict(),
            "description": self.description,
            "nullable": self.nullable,
            "is_primary_key": self.is_primary_key,
            "is_foreign_key": self.is_foreign_key,
            "default_value": self.default_value,
            "tags": list(self.tags),
            "custom_properties": dict(self.custom_properties)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaField":
        return cls(
            name=data["name"],
            type=SchemaFieldDataType.from_dict(data["type"]),
            description=data.get("description"),
            nullable=data.get("nullable", True),
            is_primary_key=data.get("is_primary_key", False),
            is_foreign_key=data.get("is_foreign_key", False),
            default_value=data.get("default_value"),
            tags=set(data.get("tags", [])),
            custom_properties=data.get("custom_properties", {})
        )


@dataclass
class SchemaMetadata:
    """Represents complete schema metadata."""
    name: str
    version: int
    platform: str
    fields: List[SchemaField] = field(default_factory=list)
    hash: Optional[str] = None
    created_time: Optional[datetime] = None
    last_modified_time: Optional[datetime] = field(default_factory=datetime.now)
    primary_keys: List[str] = field(default_factory=list)
    foreign_keys: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate schema metadata."""
        if not self.name:
            raise ValueError("Schema name is required")
        if not self.platform:
            raise ValueError("Platform is required")

    def add_field(self, field: SchemaField) -> None:
        """Add field to schema."""
        # Check for duplicate field names
        existing_names = {f.name for f in self.fields}
        if field.name in existing_names:
            raise ValueError(f"Field {field.name} already exists in schema")

        self.fields.append(field)
        self.last_modified_time = datetime.now()

    def get_field(self, name: str) -> Optional[SchemaField]:
        """Get field by name."""
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def remove_field(self, name: str) -> bool:
        """Remove field by name."""
        for i, field in enumerate(self.fields):
            if field.name == name:
                self.fields.pop(i)
                self.last_modified_time = datetime.now()
                return True
        return False

    def get_primary_key_fields(self) -> List[SchemaField]:
        """Get all primary key fields."""
        return [field for field in self.fields if field.is_primary_key]

    def get_foreign_key_fields(self) -> List[SchemaField]:
        """Get all foreign key fields."""
        return [field for field in self.fields if field.is_foreign_key]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "platform": self.platform,
            "fields": [field.to_dict() for field in self.fields],
            "hash": self.hash,
            "created_time": self.created_time.isoformat() if self.created_time else None,
            "last_modified_time": self.last_modified_time.isoformat() if self.last_modified_time else None,
            "primary_keys": self.primary_keys,
            "foreign_keys": self.foreign_keys,
            "field_count": len(self.fields)
        }


# =====================
# CONSTRAINT CLASSES
# =====================

@dataclass
class ForeignKeyConstraint:
    """Represents a foreign key constraint."""
    name: str
    column_names: List[str]
    referenced_table: str
    referenced_columns: List[str]
    on_delete: Optional[str] = None  # CASCADE, RESTRICT, SET NULL, etc.
    on_update: Optional[str] = None

    def __post_init__(self):
        """Validate foreign key constraint."""
        if not self.name:
            raise ValueError("Constraint name is required")
        if not self.column_names:
            raise ValueError("Column names are required")
        if not self.referenced_table:
            raise ValueError("Referenced table is required")
        if not self.referenced_columns:
            raise ValueError("Referenced columns are required")
        if len(self.column_names) != len(self.referenced_columns):
            raise ValueError("Column count must match referenced column count")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "column_names": self.column_names,
            "referenced_table": self.referenced_table,
            "referenced_columns": self.referenced_columns,
            "on_delete": self.on_delete,
            "on_update": self.on_update
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ForeignKeyConstraint":
        return cls(
            name=data["name"],
            column_names=data["column_names"],
            referenced_table=data["referenced_table"],
            referenced_columns=data["referenced_columns"],
            on_delete=data.get("on_delete"),
            on_update=data.get("on_update")
        )


# =====================
# TAG AND METADATA CLASSES
# =====================

@dataclass
class GlobalTags:
    """Represents global tags for entities."""
    tags: List[str] = field(default_factory=list)

    def add_tag(self, tag: str) -> None:
        """Add tag if not already present."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> bool:
        """Remove tag if present."""
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """Check if tag exists."""
        return tag in self.tags

    def clear_tags(self) -> None:
        """Remove all tags."""
        self.tags.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {"tags": self.tags}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GlobalTags":
        return cls(tags=data.get("tags", []))


@dataclass
class TagAssociation:
    """Represents association between tags and entities."""
    tag_name: str
    entity_urn: str
    associated_by: Optional[str] = None
    association_time: Optional[datetime] = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate tag association."""
        if not self.tag_name:
            raise ValueError("Tag name is required")
        if not self.entity_urn:
            raise ValueError("Entity URN is required")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag_name": self.tag_name,
            "entity_urn": self.entity_urn,
            "associated_by": self.associated_by,
            "association_time": self.association_time.isoformat() if self.association_time else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TagAssociation":
        association_time = None
        if data.get("association_time"):
            association_time = datetime.fromisoformat(data["association_time"])

        return cls(
            tag_name=data["tag_name"],
            entity_urn=data["entity_urn"],
            associated_by=data.get("associated_by"),
            association_time=association_time
        )


# =====================
# STATUS AND PROPERTIES CLASSES
# =====================

@dataclass
class Status:
    """Represents entity status information."""
    removed: bool = False
    status: str = "ACTIVE"
    actor: Optional[str] = None
    timestamp: Optional[datetime] = field(default_factory=datetime.now)
    message: Optional[str] = None

    def mark_removed(self, actor: Optional[str] = None, message: Optional[str] = None) -> None:
        """Mark entity as removed."""
        self.removed = True
        self.status = "REMOVED"
        self.actor = actor
        self.message = message
        self.timestamp = datetime.now()

    def mark_active(self, actor: Optional[str] = None, message: Optional[str] = None) -> None:
        """Mark entity as active."""
        self.removed = False
        self.status = "ACTIVE"
        self.actor = actor
        self.message = message
        self.timestamp = datetime.now()

    def mark_deprecated(self, actor: Optional[str] = None, message: Optional[str] = None) -> None:
        """Mark entity as deprecated."""
        self.status = "DEPRECATED"
        self.actor = actor
        self.message = message
        self.timestamp = datetime.now()

    def is_active(self) -> bool:
        """Check if entity is active."""
        return not self.removed and self.status == "ACTIVE"

    def is_removed(self) -> bool:
        """Check if entity is removed."""
        return self.removed or self.status == "REMOVED"

    def is_deprecated(self) -> bool:
        """Check if entity is deprecated."""
        return self.status == "DEPRECATED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "removed": self.removed,
            "status": self.status,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "message": self.message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Status":
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])

        return cls(
            removed=data.get("removed", False),
            status=data.get("status", "ACTIVE"),
            actor=data.get("actor"),
            timestamp=timestamp,
            message=data.get("message")
        )


@dataclass
class DatasetProperties:
    """Represents dataset properties and metadata."""
    name: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_properties: Dict[str, str] = field(default_factory=dict)
    external_url: Optional[str] = None
    created: Optional[datetime] = None
    last_modified: Optional[datetime] = field(default_factory=datetime.now)

    def add_tag(self, tag: str) -> None:
        """Add tag to dataset."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.last_modified = datetime.now()

    def remove_tag(self, tag: str) -> bool:
        """Remove tag from dataset."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.last_modified = datetime.now()
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """Check if dataset has tag."""
        return tag in self.tags

    def set_property(self, key: str, value: str) -> None:
        """Set custom property."""
        self.custom_properties[key] = value
        self.last_modified = datetime.now()

    def get_property(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get custom property."""
        return self.custom_properties.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "custom_properties": dict(self.custom_properties),
            "external_url": self.external_url,
            "created": self.created.isoformat() if self.created else None,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetProperties":
        created = None
        last_modified = None

        if data.get("created"):
            created = datetime.fromisoformat(data["created"])
        if data.get("last_modified"):
            last_modified = datetime.fromisoformat(data["last_modified"])

        return cls(
            name=data.get("name"),
            description=data.get("description"),
            tags=data.get("tags", []),
            custom_properties=data.get("custom_properties", {}),
            external_url=data.get("external_url"),
            created=created,
            last_modified=last_modified
        )


@dataclass
class ViewProperties:
    """Represents view-specific properties."""
    materialized: bool = False
    view_definition: Optional[str] = None
    view_language: str = "SQL"
    properties: Dict[str, Any] = field(default_factory=dict)

    def set_property(self, key: str, value: Any) -> None:
        """Set view property."""
        self.properties[key] = value

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get view property."""
        return self.properties.get(key, default)

    def is_materialized(self) -> bool:
        """Check if view is materialized."""
        return self.materialized

    def to_dict(self) -> Dict[str, Any]:
        return {
            "materialized": self.materialized,
            "view_definition": self.view_definition,
            "view_language": self.view_language,
            "properties": dict(self.properties)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ViewProperties":
        return cls(
            materialized=data.get("materialized", False),
            view_definition=data.get("view_definition"),
            view_language=data.get("view_language", "SQL"),
            properties=data.get("properties", {})
        )


# =====================
# DATABASE-SPECIFIC CLASSES
# =====================

@dataclass
class MySqlDDL:
    """Represents MySQL-specific DDL statements."""
    statement: str
    statement_type: str = "UNKNOWN"  # CREATE, ALTER, DROP, etc.
    table_name: Optional[str] = None
    schema_name: Optional[str] = None

    def __post_init__(self):
        """Parse DDL statement for metadata."""
        if not self.statement:
            raise ValueError("DDL statement is required")

        # Basic parsing to extract statement type
        statement_upper = self.statement.strip().upper()
        if statement_upper.startswith("CREATE"):
            self.statement_type = "CREATE"
        elif statement_upper.startswith("ALTER"):
            self.statement_type = "ALTER"
        elif statement_upper.startswith("DROP"):
            self.statement_type = "DROP"
        elif statement_upper.startswith("RENAME"):
            self.statement_type = "RENAME"

    def is_create_statement(self) -> bool:
        """Check if this is a CREATE statement."""
        return self.statement_type == "CREATE"

    def is_alter_statement(self) -> bool:
        """Check if this is an ALTER statement."""
        return self.statement_type == "ALTER"

    def is_drop_statement(self) -> bool:
        """Check if this is a DROP statement."""
        return self.statement_type == "DROP"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statement": self.statement,
            "statement_type": self.statement_type,
            "table_name": self.table_name,
            "schema_name": self.schema_name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MySqlDDL":
        return cls(
            statement=data["statement"],
            statement_type=data.get("statement_type", "UNKNOWN"),
            table_name=data.get("table_name"),
            schema_name=data.get("schema_name")
        )


# =====================
# METADATA EVENT CLASS
# =====================

@dataclass
class MetadataEvent:
    """
    Comprehensive metadata event with rich context and tracking information.

    Provides structured event data for monitoring, debugging, and analytics
    across all DataGuild metadata operations.
    """

    # Required core fields
    event_type: MetadataEventType
    timestamp: datetime
    source: str

    # Auto-generated and optional identification
    event_id: str = field(default_factory=lambda: str(uuid4()))
    severity: MetadataEventSeverity = MetadataEventSeverity.INFO
    message: Optional[str] = None

    # Context and correlation
    work_unit_id: Optional[str] = None
    batch_id: Optional[str] = None
    entity_urn: Optional[str] = None
    platform: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None

    # Event payload and metadata
    payload: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    # Error and diagnostic information
    error_code: Optional[str] = None
    error_details: Optional[str] = None
    stack_trace: Optional[str] = None

    # Processing and infrastructure context
    processing_node: Optional[str] = None
    thread_id: Optional[str] = None
    process_id: Optional[int] = None

    # Performance and resource metrics
    duration_ms: Optional[int] = None
    bytes_processed: Optional[int] = None
    records_processed: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

    # Retry and failure tracking
    retry_count: Optional[int] = None
    max_retries: Optional[int] = None

    # User and security context
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None

    def __post_init__(self):
        """Post-initialization validation and normalization."""
        # Validate required fields
        if not self.source:
            raise ValueError("Event source is required")

        if not isinstance(self.timestamp, datetime):
            raise ValueError("Timestamp must be a datetime object")

        # Handle string-based enum inputs
        if isinstance(self.event_type, str):
            self.event_type = MetadataEventType.from_string(self.event_type)

        if isinstance(self.severity, str):
            self.severity = MetadataEventSeverity.from_string(self.severity)

        # Generate event ID if not provided
        if not self.event_id:
            self.event_id = str(uuid4())

        # Validate URN format if provided
        if self.entity_urn and not self.entity_urn.startswith("urn:li:"):
            logger.warning(f"Invalid URN format: {self.entity_urn}")

    def is_error(self) -> bool:
        """Check if this is an error or critical event."""
        return self.severity.is_error_level()

    def is_warning_or_above(self) -> bool:
        """Check if this is a warning, error, or critical event."""
        return self.severity.is_warning_or_above()

    def is_lifecycle_event(self) -> bool:
        """Check if this is a work unit or batch lifecycle event."""
        lifecycle_events = {
            MetadataEventType.WORK_UNIT_CREATED,
            MetadataEventType.WORK_UNIT_STARTED,
            MetadataEventType.WORK_UNIT_COMPLETED,
            MetadataEventType.WORK_UNIT_FAILED,
            MetadataEventType.WORK_UNIT_RETRYING,
            MetadataEventType.WORK_UNIT_CANCELLED,
            MetadataEventType.WORK_UNIT_TIMEOUT,
            MetadataEventType.BATCH_CREATED,
            MetadataEventType.BATCH_STARTED,
            MetadataEventType.BATCH_COMPLETED,
            MetadataEventType.BATCH_FAILED,
            MetadataEventType.BATCH_TIMEOUT,
            MetadataEventType.BATCH_CANCELLED,
        }
        return self.event_type in lifecycle_events

    def is_entity_event(self) -> bool:
        """Check if this is an entity-related event."""
        entity_events = {
            MetadataEventType.ENTITY_DISCOVERED,
            MetadataEventType.ENTITY_CREATED,
            MetadataEventType.ENTITY_UPDATED,
            MetadataEventType.ENTITY_DELETED,
            MetadataEventType.ENTITY_RESTORED,
            MetadataEventType.ENTITY_DEPRECATED,
        }
        return self.event_type in entity_events

    def is_schema_event(self) -> bool:
        """Check if this is a schema-related event."""
        schema_events = {
            MetadataEventType.SCHEMA_DISCOVERED,
            MetadataEventType.SCHEMA_CHANGED,
            MetadataEventType.SCHEMA_DRIFT_DETECTED,
            MetadataEventType.SCHEMA_VALIDATED,
            MetadataEventType.SCHEMA_MIGRATION,
        }
        return self.event_type in schema_events

    def is_connection_event(self) -> bool:
        """Check if this is a connection-related event."""
        connection_events = {
            MetadataEventType.CONNECTION_ESTABLISHED,
            MetadataEventType.CONNECTION_LOST,
            MetadataEventType.CONNECTION_RETRY,
            MetadataEventType.CONNECTION_TIMEOUT,
        }
        return self.event_type in connection_events

    def get_age_seconds(self) -> float:
        """Get the age of the event in seconds."""
        return (datetime.now() - self.timestamp).total_seconds()

    def get_duration_seconds(self) -> Optional[float]:
        """Get event duration in seconds."""
        if self.duration_ms is not None:
            return self.duration_ms / 1000.0
        return None

    def add_tag(self, tag: str) -> None:
        """Add a tag to the event."""
        if tag:
            self.tags.add(tag.strip())

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the event."""
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """Check if event has a specific tag."""
        return tag in self.tags

    def add_tags(self, tags: List[str]) -> None:
        """Add multiple tags to the event."""
        for tag in tags:
            self.add_tag(tag)

    def set_payload_data(self, key: str, value: Any) -> None:
        """Set data in the event payload."""
        self.payload[key] = value

    def get_payload_data(self, key: str, default: Any = None) -> Any:
        """Get data from the event payload."""
        return self.payload.get(key, default)

    def update_payload(self, data: Dict[str, Any]) -> None:
        """Update payload with dictionary data."""
        self.payload.update(data)

    def set_error_info(
            self,
            error_code: str,
            error_details: str,
            stack_trace: Optional[str] = None,
            auto_severity: bool = True
    ) -> None:
        """
        Set error information for the event.

        Args:
            error_code: Structured error code
            error_details: Human-readable error description
            stack_trace: Optional stack trace information
            auto_severity: Whether to automatically set severity to ERROR
        """
        self.error_code = error_code
        self.error_details = error_details
        self.stack_trace = stack_trace

        if auto_severity and self.severity not in {
            MetadataEventSeverity.ERROR,
            MetadataEventSeverity.CRITICAL
        }:
            self.severity = MetadataEventSeverity.ERROR

    def set_performance_metrics(
            self,
            duration_ms: Optional[int] = None,
            bytes_processed: Optional[int] = None,
            records_processed: Optional[int] = None,
            memory_usage_mb: Optional[float] = None,
            cpu_usage_percent: Optional[float] = None
    ) -> None:
        """Set performance metrics for the event."""
        if duration_ms is not None:
            self.duration_ms = duration_ms
        if bytes_processed is not None:
            self.bytes_processed = bytes_processed
        if records_processed is not None:
            self.records_processed = records_processed
        if memory_usage_mb is not None:
            self.memory_usage_mb = memory_usage_mb
        if cpu_usage_percent is not None:
            self.cpu_usage_percent = cpu_usage_percent

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "severity": self.severity.value,
            "message": self.message,

            # Context and correlation
            "work_unit_id": self.work_unit_id,
            "batch_id": self.batch_id,
            "entity_urn": self.entity_urn,
            "platform": self.platform,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,

            # Payload and metadata
            "payload": dict(self.payload),
            "tags": sorted(list(self.tags)),

            # Error information
            "error_code": self.error_code,
            "error_details": self.error_details,
            "stack_trace": self.stack_trace,

            # Processing context
            "processing_node": self.processing_node,
            "thread_id": self.thread_id,
            "process_id": self.process_id,

            # Performance metrics
            "duration_ms": self.duration_ms,
            "duration_seconds": self.get_duration_seconds(),
            "bytes_processed": self.bytes_processed,
            "records_processed": self.records_processed,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,

            # Retry information
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,

            # User context
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,

            # Computed fields
            "age_seconds": self.get_age_seconds(),
            "is_error": self.is_error(),
            "is_warning_or_above": self.is_warning_or_above(),
            "is_lifecycle_event": self.is_lifecycle_event(),
            "is_entity_event": self.is_entity_event(),
            "is_schema_event": self.is_schema_event(),
            "is_connection_event": self.is_connection_event(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetadataEvent":
        """Create MetadataEvent from dictionary."""
        # Parse timestamp
        timestamp = datetime.fromisoformat(data["timestamp"])

        # Parse enums
        event_type = MetadataEventType.from_string(data["event_type"])
        severity = MetadataEventSeverity.from_string(data.get("severity", "info"))

        # Parse tags
        tags = set(data.get("tags", []))

        return cls(
            event_type=event_type,
            timestamp=timestamp,
            source=data["source"],
            event_id=data.get("event_id"),
            severity=severity,
            message=data.get("message"),
            work_unit_id=data.get("work_unit_id"),
            batch_id=data.get("batch_id"),
            entity_urn=data.get("entity_urn"),
            platform=data.get("platform"),
            session_id=data.get("session_id"),
            correlation_id=data.get("correlation_id"),
            payload=data.get("payload", {}),
            tags=tags,
            error_code=data.get("error_code"),
            error_details=data.get("error_details"),
            stack_trace=data.get("stack_trace"),
            processing_node=data.get("processing_node"),
            thread_id=data.get("thread_id"),
            process_id=data.get("process_id"),
            duration_ms=data.get("duration_ms"),
            bytes_processed=data.get("bytes_processed"),
            records_processed=data.get("records_processed"),
            memory_usage_mb=data.get("memory_usage_mb"),
            cpu_usage_percent=data.get("cpu_usage_percent"),
            retry_count=data.get("retry_count"),
            max_retries=data.get("max_retries"),
            user_id=data.get("user_id"),
            tenant_id=data.get("tenant_id")
        )

    @classmethod
    def create_work_unit_event(
            cls,
            event_type: MetadataEventType,
            work_unit_id: str,
            source: str,
            message: Optional[str] = None,
            severity: MetadataEventSeverity = MetadataEventSeverity.INFO,
            **kwargs
    ) -> "MetadataEvent":
        """Factory method to create work unit lifecycle events."""
        return cls(
            event_type=event_type,
            timestamp=datetime.now(),
            source=source,
            work_unit_id=work_unit_id,
            message=message,
            severity=severity,
            **kwargs
        )

    @classmethod
    def create_error_event(
            cls,
            source: str,
            error_code: str,
            error_details: str,
            work_unit_id: Optional[str] = None,
            entity_urn: Optional[str] = None,
            stack_trace: Optional[str] = None,
            severity: MetadataEventSeverity = MetadataEventSeverity.ERROR,
            **kwargs
    ) -> "MetadataEvent":
        """Factory method to create error events."""
        event = cls(
            event_type=MetadataEventType.VALIDATION_ERROR,
            timestamp=datetime.now(),
            source=source,
            severity=severity,
            work_unit_id=work_unit_id,
            entity_urn=entity_urn,
            **kwargs
        )
        event.set_error_info(error_code, error_details, stack_trace, auto_severity=False)
        return event

    @classmethod
    def create_entity_event(
            cls,
            event_type: MetadataEventType,
            entity_urn: str,
            source: str,
            platform: Optional[str] = None,
            message: Optional[str] = None,
            severity: MetadataEventSeverity = MetadataEventSeverity.INFO,
            **kwargs
    ) -> "MetadataEvent":
        """Factory method to create entity-related events."""
        return cls(
            event_type=event_type,
            timestamp=datetime.now(),
            source=source,
            entity_urn=entity_urn,
            platform=platform,
            message=message,
            severity=severity,
            **kwargs
        )

    @classmethod
    def create_performance_event(
            cls,
            source: str,
            message: str,
            duration_ms: Optional[int] = None,
            bytes_processed: Optional[int] = None,
            records_processed: Optional[int] = None,
            **kwargs
    ) -> "MetadataEvent":
        """Factory method to create performance monitoring events."""
        event = cls(
            event_type=MetadataEventType.DATA_PROFILING_COMPLETED,
            timestamp=datetime.now(),
            source=source,
            message=message,
            **kwargs
        )
        event.set_performance_metrics(
            duration_ms=duration_ms,
            bytes_processed=bytes_processed,
            records_processed=records_processed
        )
        return event

    def to_json(self, indent: Optional[int] = None) -> str:
        """Serialize event to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "MetadataEvent":
        """Create MetadataEvent from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"MetadataEvent(id={self.event_id}, type={self.event_type.value}, "
            f"severity={self.severity.value}, source={self.source})"
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"[{self.severity.value.upper()}] {self.event_type.value} "
            f"from {self.source}: {self.message or 'No message'}"
        )


# =====================
# EXPORTS
# =====================

# Export all classes and enums
__all__ = [
    # Event System
    'MetadataEventType',
    'MetadataEventSeverity',
    'MetadataEvent',

    # Data Types
    'ArrayType',
    'BooleanType',
    'BytesType',
    'DateType',
    'NullType',
    'NumberType',
    'RecordType',
    'StringType',
    'SubTypes',
    'TimeType',
    'TimeStamp',

    # Schema Classes
    'SchemaField',
    'SchemaFieldDataType',
    'SchemaMetadata',

    # Constraint Classes
    'ForeignKeyConstraint',

    # Tag and Metadata Classes
    'GlobalTags',
    'TagAssociation',

    # Status and Properties
    'Status',
    'DatasetProperties',
    'ViewProperties',

    # Database-specific Classes
    'MySqlDDL',
]
