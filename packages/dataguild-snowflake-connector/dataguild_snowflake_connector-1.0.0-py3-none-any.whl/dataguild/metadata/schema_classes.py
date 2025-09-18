"""
DataGuild metadata schema classes.

This module provides schema classes for various metadata aspects
that can be attached to entities in the DataGuild metadata system,
including comprehensive lineage tracking capabilities and operation monitoring.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, List, Union
from dataclasses import dataclass, field

import pydantic
from pydantic import Field

from dataguild.configuration.common import ConfigModel

logger = logging.getLogger(__name__)


class EntityStatus(Enum):
    """Enumeration of possible entity statuses."""
    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class DatasetLineageTypeClass(Enum):
    """
    ✅ ADDED: Enumeration of dataset lineage types for data lineage tracking.

    Represents the different types of datasets that can participate
    in data lineage relationships within the DataGuild system.
    """
    TABLE = "TABLE"
    VIEW = "VIEW"
    EXTERNAL_TABLE = "EXTERNAL_TABLE"
    MATERIALIZED_VIEW = "MATERIALIZED_VIEW"
    STREAM = "STREAM"
    STAGE = "STAGE"
    PIPE = "PIPE"
    TASK = "TASK"
    STORED_PROCEDURE = "STORED_PROCEDURE"
    FUNCTION = "FUNCTION"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, value: str) -> "DatasetLineageTypeClass":
        """
        Create DatasetLineageTypeClass from string value.

        Args:
            value: String value to convert

        Returns:
            DatasetLineageTypeClass enum value, defaults to UNKNOWN if not found
        """
        if not value:
            return cls.UNKNOWN

        try:
            return cls(value.upper())
        except ValueError:
            logger.warning(f"Unknown lineage type: {value}, defaulting to UNKNOWN")
            return cls.UNKNOWN


class OperationTypeClass(Enum):
    """
    ✅ ADDED: Enumeration of operation types for tracking database operations.

    Represents the different types of operations that can be performed
    on datasets and other entities within the DataGuild system.
    """
    # DDL Operations (Data Definition Language)
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    RENAME = "RENAME"
    TRUNCATE = "TRUNCATE"

    # DML Operations (Data Manipulation Language)
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    MERGE = "MERGE"
    COPY = "COPY"

    # DQL Operations (Data Query Language)
    SELECT = "SELECT"

    # Administrative Operations
    GRANT = "GRANT"
    REVOKE = "REVOKE"
    ANALYZE = "ANALYZE"
    VACUUM = "VACUUM"

    # Data Movement Operations
    LOAD = "LOAD"
    UNLOAD = "UNLOAD"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"

    # Snowflake-specific Operations
    CLONE = "CLONE"
    SWAP = "SWAP"
    UNDROP = "UNDROP"

    # Generic/Unknown Operations
    CUSTOM = "CUSTOM"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, value: str) -> "OperationTypeClass":
        """
        Create OperationTypeClass from string value.

        Args:
            value: String value to convert

        Returns:
            OperationTypeClass enum value, defaults to UNKNOWN if not found
        """
        if not value:
            return cls.UNKNOWN

        try:
            return cls(value.upper())
        except ValueError:
            logger.warning(f"Unknown operation type: {value}, defaulting to UNKNOWN")
            return cls.UNKNOWN

    def is_ddl(self) -> bool:
        """Check if this operation is a DDL operation."""
        return self in {
            self.CREATE, self.DROP, self.ALTER, self.RENAME, self.TRUNCATE
        }

    def is_dml(self) -> bool:
        """Check if this operation is a DML operation."""
        return self in {
            self.INSERT, self.UPDATE, self.DELETE, self.MERGE, self.COPY
        }

    def is_dql(self) -> bool:
        """Check if this operation is a DQL operation."""
        return self == self.SELECT

    def is_administrative(self) -> bool:
        """Check if this operation is administrative."""
        return self in {
            self.GRANT, self.REVOKE, self.ANALYZE, self.VACUUM
        }

    def is_data_movement(self) -> bool:
        """Check if this operation involves data movement."""
        return self in {
            self.LOAD, self.UNLOAD, self.IMPORT, self.EXPORT, self.COPY
        }


@dataclass
class OperationClass:
    """
    ✅ ADDED: Represents a database operation performed on an entity.

    Tracks operations performed on datasets and other entities, providing
    comprehensive audit trail and operational metadata for governance and monitoring.
    """

    # Required fields
    operation_type: OperationTypeClass
    actor: str  # User or system that performed the operation
    timestamp: datetime

    # Optional operation details
    entity_urn: Optional[str] = None  # URN of the entity affected
    source_entity_urn: Optional[str] = None  # Source entity for operations like COPY, CLONE
    target_entity_urn: Optional[str] = None  # Target entity for operations like RENAME

    # Operation context
    operation_id: Optional[str] = None  # Unique identifier for the operation
    session_id: Optional[str] = None  # Database session identifier
    query_id: Optional[str] = None  # Query identifier if applicable

    # Operation metadata
    sql_statement: Optional[str] = None  # SQL statement that triggered the operation
    affected_rows: Optional[int] = None  # Number of rows affected
    duration_ms: Optional[int] = None  # Operation duration in milliseconds

    # Status and result
    status: str = "SUCCESS"  # SUCCESS, FAILED, PENDING, CANCELLED
    error_message: Optional[str] = None  # Error message if operation failed

    # Additional metadata
    properties: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    # Audit information
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    last_modified_at: Optional[datetime] = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization validation and normalization."""
        # Handle string-based operation type input
        if isinstance(self.operation_type, str):
            self.operation_type = OperationTypeClass.from_string(self.operation_type)

        # Validate required fields
        if not self.actor:
            raise ValueError("Actor must be specified")

        if not isinstance(self.timestamp, datetime):
            raise ValueError("Timestamp must be a datetime object")

        # Validate status
        valid_statuses = {"SUCCESS", "FAILED", "PENDING", "CANCELLED"}
        if self.status.upper() not in valid_statuses:
            logger.warning(f"Invalid status: {self.status}, setting to SUCCESS")
            self.status = "SUCCESS"
        else:
            self.status = self.status.upper()

        # Validate URN formats if provided
        for urn_field, urn_value in [
            ("entity_urn", self.entity_urn),
            ("source_entity_urn", self.source_entity_urn),
            ("target_entity_urn", self.target_entity_urn)
        ]:
            if urn_value and not urn_value.startswith("urn:li:"):
                raise ValueError(f"Invalid URN format for {urn_field}: {urn_value}")

        # Set last_modified_at if not provided
        if self.last_modified_at is None:
            self.last_modified_at = datetime.now()

    def is_successful(self) -> bool:
        """Check if the operation was successful."""
        return self.status == "SUCCESS"

    def is_failed(self) -> bool:
        """Check if the operation failed."""
        return self.status == "FAILED"

    def is_pending(self) -> bool:
        """Check if the operation is pending."""
        return self.status == "PENDING"

    def mark_success(self, affected_rows: Optional[int] = None, duration_ms: Optional[int] = None) -> None:
        """
        Mark the operation as successful.

        Args:
            affected_rows: Number of rows affected by the operation
            duration_ms: Operation duration in milliseconds
        """
        self.status = "SUCCESS"
        self.error_message = None

        if affected_rows is not None:
            self.affected_rows = affected_rows
        if duration_ms is not None:
            self.duration_ms = duration_ms

        self.last_modified_at = datetime.now()

    def mark_failed(self, error_message: str, duration_ms: Optional[int] = None) -> None:
        """
        Mark the operation as failed.

        Args:
            error_message: Error message describing the failure
            duration_ms: Operation duration in milliseconds
        """
        self.status = "FAILED"
        self.error_message = error_message

        if duration_ms is not None:
            self.duration_ms = duration_ms

        self.last_modified_at = datetime.now()

    def set_property(self, key: str, value: str) -> None:
        """
        Set a custom property for this operation.

        Args:
            key: Property key
            value: Property value
        """
        self.properties[key] = value
        self.last_modified_at = datetime.now()

    def get_property(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a custom property value.

        Args:
            key: Property key
            default: Default value if key not found

        Returns:
            Property value or default
        """
        return self.properties.get(key, default)

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to this operation.

        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.last_modified_at = datetime.now()

    def remove_tag(self, tag: str) -> bool:
        """
        Remove a tag from this operation.

        Args:
            tag: Tag to remove

        Returns:
            True if tag was found and removed, False otherwise
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.last_modified_at = datetime.now()
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        """
        Check if operation has a specific tag.

        Args:
            tag: Tag to check for

        Returns:
            True if tag exists, False otherwise
        """
        return tag in self.tags

    def get_operation_category(self) -> str:
        """Get the category of this operation (DDL, DML, DQL, etc.)."""
        if self.operation_type.is_ddl():
            return "DDL"
        elif self.operation_type.is_dml():
            return "DML"
        elif self.operation_type.is_dql():
            return "DQL"
        elif self.operation_type.is_administrative():
            return "ADMINISTRATIVE"
        elif self.operation_type.is_data_movement():
            return "DATA_MOVEMENT"
        else:
            return "OTHER"

    def get_duration_seconds(self) -> Optional[float]:
        """Get operation duration in seconds."""
        if self.duration_ms is not None:
            return self.duration_ms / 1000.0
        return None

    def affects_schema(self) -> bool:
        """Check if this operation affects schema structure."""
        schema_affecting_ops = {
            OperationTypeClass.CREATE, OperationTypeClass.DROP,
            OperationTypeClass.ALTER, OperationTypeClass.RENAME
        }
        return self.operation_type in schema_affecting_ops

    def affects_data(self) -> bool:
        """Check if this operation affects data content."""
        data_affecting_ops = {
            OperationTypeClass.INSERT, OperationTypeClass.UPDATE,
            OperationTypeClass.DELETE, OperationTypeClass.MERGE,
            OperationTypeClass.COPY, OperationTypeClass.LOAD,
            OperationTypeClass.TRUNCATE
        }
        return self.operation_type in data_affecting_ops

    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary representation."""
        return {
            "operation_type": self.operation_type.value,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat(),
            "entity_urn": self.entity_urn,
            "source_entity_urn": self.source_entity_urn,
            "target_entity_urn": self.target_entity_urn,
            "operation_id": self.operation_id,
            "session_id": self.session_id,
            "query_id": self.query_id,
            "sql_statement": self.sql_statement,
            "affected_rows": self.affected_rows,
            "duration_ms": self.duration_ms,
            "duration_seconds": self.get_duration_seconds(),
            "status": self.status,
            "error_message": self.error_message,
            "properties": dict(self.properties),
            "tags": self.tags.copy(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_modified_at": self.last_modified_at.isoformat() if self.last_modified_at else None,
            "operation_category": self.get_operation_category(),
            "is_successful": self.is_successful(),
            "affects_schema": self.affects_schema(),
            "affects_data": self.affects_data()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationClass":
        """Create OperationClass from dictionary."""
        # Parse datetime fields
        timestamp = datetime.fromisoformat(data["timestamp"])
        created_at = None
        last_modified_at = None

        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        if data.get("last_modified_at"):
            last_modified_at = datetime.fromisoformat(data["last_modified_at"])

        return cls(
            operation_type=OperationTypeClass.from_string(data["operation_type"]),
            actor=data["actor"],
            timestamp=timestamp,
            entity_urn=data.get("entity_urn"),
            source_entity_urn=data.get("source_entity_urn"),
            target_entity_urn=data.get("target_entity_urn"),
            operation_id=data.get("operation_id"),
            session_id=data.get("session_id"),
            query_id=data.get("query_id"),
            sql_statement=data.get("sql_statement"),
            affected_rows=data.get("affected_rows"),
            duration_ms=data.get("duration_ms"),
            status=data.get("status", "SUCCESS"),
            error_message=data.get("error_message"),
            properties=data.get("properties", {}),
            tags=data.get("tags", []),
            created_at=created_at,
            last_modified_at=last_modified_at
        )

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (f"OperationClass(type={self.operation_type.value}, "
                f"actor={self.actor}, status={self.status}, "
                f"entity={self.entity_urn})")


@dataclass
class UpstreamClass:
    """
    ✅ ADDED: Represents an upstream lineage relationship in DataGuild.

    Tracks upstream dependencies for datasets, including the source entity,
    relationship type, and temporal information about the lineage.
    """

    # Required fields
    urn: str
    type: str

    # Optional lineage metadata
    lineage_type: DatasetLineageTypeClass = DatasetLineageTypeClass.UNKNOWN

    # Temporal information (Unix timestamps in milliseconds)
    created_audit_stamp: Optional[int] = None
    last_modified_audit_stamp: Optional[int] = None

    # Lineage confidence and source information
    confidence_score: float = 1.0
    source_system: Optional[str] = None

    # Additional metadata
    properties: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and normalization."""
        # Handle string-based lineage type input
        if isinstance(self.lineage_type, str):
            self.lineage_type = DatasetLineageTypeClass.from_string(self.lineage_type)

        # Validate URN format
        if not self.urn or not isinstance(self.urn, str):
            raise ValueError("URN must be a non-empty string")

        if not self.urn.startswith("urn:li:"):
            raise ValueError(f"Invalid URN format: {self.urn}")

        # Validate confidence score
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")

        # Set default timestamps if not provided
        current_time_ms = int(datetime.now().timestamp() * 1000)
        if self.created_audit_stamp is None:
            self.created_audit_stamp = current_time_ms
        if self.last_modified_audit_stamp is None:
            self.last_modified_audit_stamp = current_time_ms

    def get_created_datetime(self) -> Optional[datetime]:
        """Get created timestamp as datetime object."""
        if self.created_audit_stamp:
            return datetime.fromtimestamp(self.created_audit_stamp / 1000)
        return None

    def get_last_modified_datetime(self) -> Optional[datetime]:
        """Get last modified timestamp as datetime object."""
        if self.last_modified_audit_stamp:
            return datetime.fromtimestamp(self.last_modified_audit_stamp / 1000)
        return None

    def update_last_modified(self) -> None:
        """Update the last modified timestamp to current time."""
        self.last_modified_audit_stamp = int(datetime.now().timestamp() * 1000)

    def set_property(self, key: str, value: str) -> None:
        """
        Set a custom property for this lineage relationship.

        Args:
            key: Property key
            value: Property value
        """
        self.properties[key] = value
        self.update_last_modified()

    def get_property(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a custom property value.

        Args:
            key: Property key
            default: Default value if key not found

        Returns:
            Property value or default
        """
        return self.properties.get(key, default)

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """
        Check if this lineage relationship has high confidence.

        Args:
            threshold: Confidence threshold (default: 0.8)

        Returns:
            True if confidence score >= threshold
        """
        return self.confidence_score >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert upstream lineage to dictionary representation."""
        return {
            "urn": self.urn,
            "type": self.type,
            "lineage_type": self.lineage_type.value,
            "created_audit_stamp": self.created_audit_stamp,
            "last_modified_audit_stamp": self.last_modified_audit_stamp,
            "confidence_score": self.confidence_score,
            "source_system": self.source_system,
            "properties": dict(self.properties),
            "created_datetime": self.get_created_datetime().isoformat() if self.get_created_datetime() else None,
            "last_modified_datetime": self.get_last_modified_datetime().isoformat() if self.get_last_modified_datetime() else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UpstreamClass":
        """Create UpstreamClass from dictionary."""
        return cls(
            urn=data["urn"],
            type=data["type"],
            lineage_type=DatasetLineageTypeClass.from_string(data.get("lineage_type", "UNKNOWN")),
            created_audit_stamp=data.get("created_audit_stamp"),
            last_modified_audit_stamp=data.get("last_modified_audit_stamp"),
            confidence_score=data.get("confidence_score", 1.0),
            source_system=data.get("source_system"),
            properties=data.get("properties", {})
        )


@dataclass
class DatasetLineageClass:
    """
    ✅ ADDED: Complete dataset lineage information including upstream and downstream relationships.
    """

    upstreams: List[UpstreamClass] = field(default_factory=list)
    fine_grained_lineages: List[Dict[str, Any]] = field(default_factory=list)

    def add_upstream(
        self,
        urn: str,
        lineage_type: Union[str, DatasetLineageTypeClass] = DatasetLineageTypeClass.UNKNOWN,
        confidence_score: float = 1.0,
        source_system: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None
    ) -> UpstreamClass:
        """
        Add an upstream lineage relationship.

        Args:
            urn: URN of the upstream entity
            lineage_type: Type of lineage relationship
            confidence_score: Confidence in this lineage relationship
            source_system: System that provided this lineage information
            properties: Additional properties for this relationship

        Returns:
            Created UpstreamClass instance
        """
        upstream = UpstreamClass(
            urn=urn,
            type="DATASET",  # Default type for dataset lineage
            lineage_type=lineage_type,
            confidence_score=confidence_score,
            source_system=source_system,
            properties=properties or {}
        )

        self.upstreams.append(upstream)
        return upstream

    def remove_upstream(self, urn: str) -> bool:
        """
        Remove an upstream lineage relationship by URN.

        Args:
            urn: URN of the upstream to remove

        Returns:
            True if upstream was found and removed, False otherwise
        """
        for i, upstream in enumerate(self.upstreams):
            if upstream.urn == urn:
                self.upstreams.pop(i)
                return True
        return False

    def get_upstream_by_urn(self, urn: str) -> Optional[UpstreamClass]:
        """
        Get upstream lineage by URN.

        Args:
            urn: URN to search for

        Returns:
            UpstreamClass if found, None otherwise
        """
        for upstream in self.upstreams:
            if upstream.urn == urn:
                return upstream
        return None

    def get_upstreams_by_type(self, lineage_type: DatasetLineageTypeClass) -> List[UpstreamClass]:
        """
        Get all upstream lineages of a specific type.

        Args:
            lineage_type: Type of lineage to filter by

        Returns:
            List of matching upstream lineages
        """
        return [upstream for upstream in self.upstreams if upstream.lineage_type == lineage_type]

    def get_high_confidence_upstreams(self, threshold: float = 0.8) -> List[UpstreamClass]:
        """
        Get upstream lineages with high confidence scores.

        Args:
            threshold: Confidence threshold

        Returns:
            List of high-confidence upstream lineages
        """
        return [upstream for upstream in self.upstreams if upstream.is_high_confidence(threshold)]

    def get_lineage_summary(self) -> Dict[str, Any]:
        """Get summary statistics for lineage relationships."""
        total_upstreams = len(self.upstreams)

        # Count by lineage type
        type_counts = {}
        confidence_scores = []

        for upstream in self.upstreams:
            lineage_type = upstream.lineage_type.value
            type_counts[lineage_type] = type_counts.get(lineage_type, 0) + 1
            confidence_scores.append(upstream.confidence_score)

        # Calculate confidence statistics
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        high_confidence_count = len(self.get_high_confidence_upstreams())

        return {
            "total_upstreams": total_upstreams,
            "upstreams_by_type": type_counts,
            "average_confidence": round(avg_confidence, 3),
            "high_confidence_count": high_confidence_count,
            "high_confidence_percentage": round(
                (high_confidence_count / total_upstreams * 100) if total_upstreams > 0 else 0, 1
            )
        }


@dataclass
class StatusClass:
    """
    Status aspect for DataGuild entities.

    Represents the current status of an entity, including whether
    it has been removed (soft deleted) or is active.
    """

    removed: bool = False
    status: EntityStatus = EntityStatus.ACTIVE
    actor: Optional[str] = None
    timestamp: Optional[datetime] = field(default_factory=datetime.now)
    message: Optional[str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        # Ensure consistency between removed flag and status
        if self.removed and self.status == EntityStatus.ACTIVE:
            self.status = EntityStatus.REMOVED
        elif not self.removed and self.status == EntityStatus.REMOVED:
            self.removed = True

    def mark_removed(self, actor: Optional[str] = None, message: Optional[str] = None) -> None:
        """
        Mark the entity as removed (soft delete).

        Args:
            actor: User or system that performed the removal
            message: Optional message explaining the removal
        """
        self.removed = True
        self.status = EntityStatus.REMOVED
        self.actor = actor
        self.message = message
        self.timestamp = datetime.now()

    def mark_active(self, actor: Optional[str] = None, message: Optional[str] = None) -> None:
        """
        Mark the entity as active (restore from soft delete).

        Args:
            actor: User or system that performed the restoration
            message: Optional message explaining the restoration
        """
        self.removed = False
        self.status = EntityStatus.ACTIVE
        self.actor = actor
        self.message = message
        self.timestamp = datetime.now()

    def mark_deprecated(self, actor: Optional[str] = None, message: Optional[str] = None) -> None:
        """
        Mark the entity as deprecated.

        Args:
            actor: User or system that performed the deprecation
            message: Optional message explaining the deprecation
        """
        self.status = EntityStatus.DEPRECATED
        self.actor = actor
        self.message = message
        self.timestamp = datetime.now()

    def is_active(self) -> bool:
        """Check if the entity is active."""
        return not self.removed and self.status == EntityStatus.ACTIVE

    def is_removed(self) -> bool:
        """Check if the entity is removed."""
        return self.removed or self.status == EntityStatus.REMOVED

    def is_deprecated(self) -> bool:
        """Check if the entity is deprecated."""
        return self.status == EntityStatus.DEPRECATED

    def to_dict(self) -> Dict[str, Any]:
        """Convert status to dictionary representation."""
        return {
            "removed": self.removed,
            "status": self.status.value,
            "actor": self.actor,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "message": self.message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusClass":
        """Create StatusClass from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])

        return cls(
            removed=data.get("removed", False),
            status=EntityStatus(data.get("status", "ACTIVE")),
            actor=data.get("actor"),
            timestamp=timestamp,
            message=data.get("message")
        )


@dataclass
class OwnershipClass:
    """Ownership aspect for DataGuild entities."""

    owners: list = field(default_factory=list)
    last_modified: Optional[datetime] = field(default_factory=datetime.now)

    def add_owner(self, owner_urn: str, owner_type: str = "USER") -> None:
        """Add an owner to the entity."""
        owner = {
            "owner": owner_urn,
            "type": owner_type,
            "source": {"type": "MANUAL"},
        }
        if owner not in self.owners:
            self.owners.append(owner)
            self.last_modified = datetime.now()


@dataclass
class DatasetPropertiesClass:
    """Dataset properties aspect for DataGuild entities."""

    name: Optional[str] = None
    description: Optional[str] = None
    tags: list = field(default_factory=list)
    custom_properties: Dict[str, str] = field(default_factory=dict)
    external_url: Optional[str] = None
    created: Optional[datetime] = None
    last_modified: Optional[datetime] = field(default_factory=datetime.now)

    def add_tag(self, tag: str) -> None:
        """Add a tag to the dataset."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.last_modified = datetime.now()

    def set_property(self, key: str, value: str) -> None:
        """Set a custom property."""
        self.custom_properties[key] = value
        self.last_modified = datetime.now()


@dataclass
class SchemaMetadataClass:
    """Schema metadata aspect for DataGuild entities."""

    schema_name: str
    platform: str
    version: int = 0
    hash: Optional[str] = None
    fields: list = field(default_factory=list)
    primary_keys: list = field(default_factory=list)
    foreign_keys: list = field(default_factory=list)

    def add_field(self, field_path: str, field_type: str, description: Optional[str] = None) -> None:
        """Add a field to the schema."""
        field_info = {
            "fieldPath": field_path,
            "type": {"type": {"com.linkedin.schema.StringType": {}}},
            "nativeDataType": field_type,
            "description": description,
            "nullable": True,
            "recursive": False
        }
        self.fields.append(field_info)


# Export all classes
__all__ = [
    # Enums
    'EntityStatus',
    'DatasetLineageTypeClass',
    'OperationTypeClass',  # ✅ ADDED

    # Schema classes
    'StatusClass',
    'OwnershipClass',
    'DatasetPropertiesClass',
    'SchemaMetadataClass',

    # Lineage classes
    'UpstreamClass',
    'DatasetLineageClass',

    # ✅ ADDED: Operation classes
    'OperationClass',
]
