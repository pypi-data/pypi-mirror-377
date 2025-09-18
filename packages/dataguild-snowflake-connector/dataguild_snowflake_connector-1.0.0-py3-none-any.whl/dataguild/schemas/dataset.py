"""
DataGuild Dataset Metadata Schemas

Dataset-specific metadata structures including lineage, ownership,
properties, and other dataset-related metadata.

Author: DataGuild Engineering Team
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime


class DatasetLineageType(Enum):
    """
    Enumeration of dataset lineage relationship types.

    Defines the nature of the relationship between upstream and downstream datasets.
    """

    COPY = "COPY"
    TRANSFORM = "TRANSFORM"
    VIEW = "VIEW"
    AGGREGATION = "AGGREGATION"
    FILTER = "FILTER"
    JOIN = "JOIN"
    UNION = "UNION"
    PIVOT = "PIVOT"
    UNPIVOT = "UNPIVOT"
    SAMPLE = "SAMPLE"
    MATERIALIZE = "MATERIALIZE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    INSERT = "INSERT"

    def __str__(self) -> str:
        """String representation of lineage type."""
        return self.value

    def is_read_only(self) -> bool:
        """Check if this lineage type represents read-only operations."""
        read_only_types = {
            self.COPY, self.TRANSFORM, self.VIEW, self.AGGREGATION,
            self.FILTER, self.JOIN, self.UNION, self.PIVOT, self.UNPIVOT,
            self.SAMPLE, self.MATERIALIZE
        }
        return self in read_only_types

    def is_modification(self) -> bool:
        """Check if this lineage type represents data modification."""
        modification_types = {self.UPDATE, self.DELETE, self.INSERT}
        return self in modification_types


@dataclass(frozen=True)
class Upstream:
    """
    Represents an upstream dataset dependency.

    Defines a dataset that serves as input/source for another dataset,
    along with the type of relationship.
    """

    dataset: str  # Dataset URN
    type: DatasetLineageType
    created: Optional[int] = None  # Unix timestamp

    def __post_init__(self):
        """Validate upstream configuration."""
        if not self.dataset:
            raise ValueError("Dataset URN cannot be empty")

        if not isinstance(self.type, DatasetLineageType):
            raise ValueError(f"Invalid lineage type: {self.type}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "dataset": self.dataset,
            "type": self.type.value
        }
        if self.created:
            result["created"] = self.created
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Upstream':
        """Create instance from dictionary."""
        return cls(
            dataset=data["dataset"],
            type=DatasetLineageType(data["type"]),
            created=data.get("created")
        )

    def get_lineage_description(self) -> str:
        """Get human-readable lineage description."""
        descriptions = {
            DatasetLineageType.COPY: "copied from",
            DatasetLineageType.TRANSFORM: "transformed from",
            DatasetLineageType.VIEW: "view of",
            DatasetLineageType.AGGREGATION: "aggregated from",
            DatasetLineageType.FILTER: "filtered from",
            DatasetLineageType.JOIN: "joined from",
            DatasetLineageType.UNION: "union of",
            DatasetLineageType.MATERIALIZE: "materialized from"
        }
        return descriptions.get(self.type, f"derived from ({self.type.value})")


@dataclass(frozen=True)
class UpstreamLineage:
    """
    Complete upstream lineage information for a dataset.

    Contains all upstream dependencies and their relationships to the target dataset.
    """

    upstreams: List[Upstream] = field(default_factory=list)
    created: Optional[int] = None  # Unix timestamp

    def __post_init__(self):
        """Validate upstream lineage."""
        if not isinstance(self.upstreams, list):
            raise ValueError("Upstreams must be a list")

        # Check for duplicate upstream datasets
        dataset_urns = [upstream.dataset for upstream in self.upstreams]
        if len(dataset_urns) != len(set(dataset_urns)):
            raise ValueError("Duplicate upstream datasets are not allowed")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "upstreams": [upstream.to_dict() for upstream in self.upstreams]
        }
        if self.created:
            result["created"] = self.created
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UpstreamLineage':
        """Create instance from dictionary."""
        return cls(
            upstreams=[Upstream.from_dict(u) for u in data.get("upstreams", [])],
            created=data.get("created")
        )

    def add_upstream(self, upstream: Upstream) -> 'UpstreamLineage':
        """Add upstream dependency (returns new instance due to frozen dataclass)."""
        if upstream.dataset not in [u.dataset for u in self.upstreams]:
            return UpstreamLineage(
                upstreams=self.upstreams + [upstream],
                created=self.created
            )
        return self

    def remove_upstream(self, dataset_urn: str) -> 'UpstreamLineage':
        """Remove upstream by dataset URN (returns new instance)."""
        new_upstreams = [u for u in self.upstreams if u.dataset != dataset_urn]
        return UpstreamLineage(upstreams=new_upstreams, created=self.created)

    def get_upstream_count(self) -> int:
        """Get the number of upstream dependencies."""
        return len(self.upstreams)

    def get_upstream_by_type(self, lineage_type: DatasetLineageType) -> List[Upstream]:
        """Get upstreams filtered by lineage type."""
        return [u for u in self.upstreams if u.type == lineage_type]

    def get_upstream_datasets(self) -> List[str]:
        """Get list of upstream dataset URNs."""
        return [upstream.dataset for upstream in self.upstreams]

    def has_upstream(self, dataset_urn: str) -> bool:
        """Check if specific upstream exists."""
        return dataset_urn in self.get_upstream_datasets()

    def get_lineage_summary(self) -> Dict[str, int]:
        """Get summary of lineage types."""
        summary = {}
        for upstream in self.upstreams:
            lineage_type = upstream.type.value
            summary[lineage_type] = summary.get(lineage_type, 0) + 1
        return summary

    def __len__(self) -> int:
        """Get the number of upstream dependencies."""
        return len(self.upstreams)


@dataclass(frozen=True)
class DatasetProperties:
    """Dataset-specific properties and metadata."""

    name: str
    qualified_name: Optional[str] = None
    description: Optional[str] = None
    custom_properties: Optional[Dict[str, str]] = None
    external_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate dataset properties."""
        if not self.name:
            raise ValueError("Dataset name cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"name": self.name}

        if self.qualified_name:
            result["qualifiedName"] = self.qualified_name
        if self.description:
            result["description"] = self.description
        if self.custom_properties:
            result["customProperties"] = self.custom_properties
        if self.external_url:
            result["externalUrl"] = self.external_url
        if self.tags:
            result["tags"] = sorted(self.tags)

        return result


@dataclass(frozen=True)
class ViewProperties:
    """View-specific properties."""

    materialized: bool
    view_language: str
    view_logic: str

    def __post_init__(self):
        """Validate view properties."""
        if not self.view_language:
            raise ValueError("View language cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "materialized": self.materialized,
            "viewLanguage": self.view_language,
            "viewLogic": self.view_logic
        }


# Utility functions for lineage operations

def create_copy_lineage(source_dataset_urn: str) -> UpstreamLineage:
    """Create simple copy lineage from source dataset."""
    upstream = Upstream(dataset=source_dataset_urn, type=DatasetLineageType.COPY)
    return UpstreamLineage(upstreams=[upstream])


def create_transform_lineage(source_datasets: List[str]) -> UpstreamLineage:
    """Create transformation lineage from multiple source datasets."""
    upstreams = [
        Upstream(dataset=urn, type=DatasetLineageType.TRANSFORM)
        for urn in source_datasets
    ]
    return UpstreamLineage(upstreams=upstreams)


def create_view_lineage(source_dataset_urn: str) -> UpstreamLineage:
    """Create view lineage from source dataset."""
    upstream = Upstream(dataset=source_dataset_urn, type=DatasetLineageType.VIEW)
    return UpstreamLineage(upstreams=[upstream])


def merge_lineage(*lineages: UpstreamLineage) -> UpstreamLineage:
    """Merge multiple upstream lineages into one."""
    all_upstreams = []
    seen_datasets = set()

    for lineage in lineages:
        for upstream in lineage.upstreams:
            if upstream.dataset not in seen_datasets:
                all_upstreams.append(upstream)
                seen_datasets.add(upstream.dataset)

    return UpstreamLineage(upstreams=all_upstreams)


# Export all classes and functions
__all__ = [
    # Enums
    'DatasetLineageType',

    # Core classes
    'Upstream',
    'UpstreamLineage',
    'DatasetProperties',
    'ViewProperties',

    # Utility functions
    'create_copy_lineage',
    'create_transform_lineage',
    'create_view_lineage',
    'merge_lineage',
]
