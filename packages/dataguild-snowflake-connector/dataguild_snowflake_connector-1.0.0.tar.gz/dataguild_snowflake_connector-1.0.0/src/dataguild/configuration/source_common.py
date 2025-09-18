"""
Common configuration mixins and base classes for data sources.

This module provides reusable configuration components that can be mixed into
data source configurations to provide common functionality like platform
instance handling, environment variable support, and dataset filtering.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Any, Union
from pydantic import BaseModel, Field, validator, root_validator

from dataguild.configuration.common import ConfigModel, AllowDenyPattern

logger = logging.getLogger(__name__)


class EnvConfigMixin(ConfigModel):
    """
    Mixin for environment-related configuration.

    Provides environment name and related functionality for multi-environment
    deployments (dev, staging, prod, etc.).
    """

    env: str = Field(
        default="PROD",
        description="Environment name (e.g., DEV, STAGING, PROD)"
    )

    @validator("env")
    def validate_env(cls, v):
        """Validate and normalize environment name."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Environment must be a non-empty string")
        return v.strip().upper()

    def is_production_env(self) -> bool:
        """Check if current environment is production."""
        return self.env.upper() in {"PROD", "PRODUCTION"}

    def is_development_env(self) -> bool:
        """Check if current environment is development."""
        return self.env.upper() in {"DEV", "DEVELOPMENT", "LOCAL"}


class PlatformInstanceConfigMixin(ConfigModel):
    """
    Mixin for platform instance configuration.

    Enables support for multiple instances of the same platform type,
    useful for multi-tenant or multi-region deployments.
    """

    platform_instance: Optional[str] = Field(
        default=None,
        description="Optional platform instance identifier for multi-instance setups"
    )

    @validator("platform_instance")
    def validate_platform_instance(cls, v):
        """Validate platform instance format."""
        if v is not None:
            if not isinstance(v, str) or not v.strip():
                raise ValueError("Platform instance must be a non-empty string if provided")
            # Basic validation - alphanumeric and common separators
            import re
            if not re.match(r'^[a-zA-Z0-9._-]+$', v.strip()):
                raise ValueError("Platform instance must contain only letters, numbers, dots, hyphens, and underscores")
            return v.strip()
        return v

    def get_platform_urn_prefix(self, platform: str) -> str:
        """Get platform URN prefix including instance if configured."""
        if self.platform_instance:
            return f"urn:li:dataPlatform:({platform},{self.platform_instance})"
        return f"urn:li:dataPlatform:{platform}"


class LowerCaseDatasetUrnConfigMixin(ConfigModel):
    """
    Mixin for dataset URN case handling configuration.

    Provides options for URN case normalization to ensure consistency
    across different data platforms and tools.
    """

    convert_urns_to_lowercase: bool = Field(
        default=True,
        description="Whether to convert dataset URNs to lowercase for consistency"
    )

    def normalize_urn(self, urn: str) -> str:
        """Normalize URN based on configuration."""
        if not isinstance(urn, str):
            return str(urn)

        if self.convert_urns_to_lowercase:
            return urn.lower()
        return urn


class DatasetFilterMixin(ConfigModel):
    """
    Mixin for dataset filtering configuration.

    Provides common dataset filtering capabilities that can be reused
    across different data source connectors.
    """

    include_tables: bool = Field(
        default=True,
        description="Whether to include tables in ingestion"
    )

    include_views: bool = Field(
        default=True,
        description="Whether to include views in ingestion"
    )

    table_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern.allow_all,
        description="Regex patterns for filtering tables"
    )

    view_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern.allow_all,
        description="Regex patterns for filtering views"
    )

    schema_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern.allow_all,
        description="Regex patterns for filtering schemas"
    )

    database_pattern: AllowDenyPattern = Field(
        default_factory=AllowDenyPattern.allow_all,
        description="Regex patterns for filtering databases"
    )

    def is_dataset_allowed(
        self,
        dataset_name: str,
        dataset_type: str = "table",
        schema_name: Optional[str] = None,
        database_name: Optional[str] = None
    ) -> bool:
        """
        Check if a dataset is allowed based on filtering configuration.

        Args:
            dataset_name: Name of the dataset
            dataset_type: Type of dataset ("table", "view", etc.)
            schema_name: Optional schema name
            database_name: Optional database name

        Returns:
            True if dataset should be included, False otherwise
        """
        # Check if dataset type is enabled
        if dataset_type.lower() == "table" and not self.include_tables:
            return False
        if dataset_type.lower() == "view" and not self.include_views:
            return False

        # Check database pattern
        if database_name and not self.database_pattern.allowed(database_name):
            return False

        # Check schema pattern
        if schema_name and not self.schema_pattern.allowed(schema_name):
            return False

        # Check dataset pattern based on type
        if dataset_type.lower() == "table":
            return self.table_pattern.allowed(dataset_name)
        elif dataset_type.lower() == "view":
            return self.view_pattern.allowed(dataset_name)

        # Default to allowed for other types
        return True


class ConnectionConfigMixin(ConfigModel):
    """
    Mixin for database connection configuration.

    Provides common connection parameters and utilities that can be
    shared across different database connectors.
    """

    connect_timeout: int = Field(
        default=30,
        description="Connection timeout in seconds",
        ge=1,
        le=300
    )

    query_timeout: int = Field(
        default=300,
        description="Query timeout in seconds",
        ge=1,
        le=3600
    )

    max_retries: int = Field(
        default=3,
        description="Maximum number of connection retry attempts",
        ge=0,
        le=10
    )

    retry_delay: float = Field(
        default=1.0,
        description="Delay between retry attempts in seconds",
        ge=0.1,
        le=60.0
    )

    connection_pool_size: int = Field(
        default=5,
        description="Maximum number of connections in pool",
        ge=1,
        le=50
    )

    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters as dictionary."""
        return {
            "connect_timeout": self.connect_timeout,
            "query_timeout": self.query_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "pool_size": self.connection_pool_size
        }


class StatefulIngestionMixin(ConfigModel):
    """
    Mixin for stateful ingestion configuration.

    Provides configuration for checkpointing, incremental processing,
    and state management across ingestion runs.
    """

    enable_stateful_ingestion: bool = Field(
        default=False,
        description="Whether to enable stateful ingestion with checkpointing"
    )

    state_provider_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Configuration for state provider (filesystem, database, etc.)"
    )

    ignore_old_state: bool = Field(
        default=False,
        description="Whether to ignore existing state and start fresh"
    )

    state_retention_days: int = Field(
        default=30,
        description="Number of days to retain state information",
        ge=1,
        le=365
    )

    def is_stateful_enabled(self) -> bool:
        """Check if stateful ingestion is enabled and properly configured."""
        return (
            self.enable_stateful_ingestion
            and not self.ignore_old_state
            and self.state_provider_config is not None
        )


class ProfilingConfigMixin(ConfigModel):
    """
    Mixin for data profiling configuration.

    Provides configuration for data profiling, statistics collection,
    and data quality analysis.
    """

    profiling_enabled: bool = Field(
        default=False,
        description="Whether to enable data profiling"
    )

    profile_table_level_only: bool = Field(
        default=True,
        description="Whether to profile only at table level (not column level)"
    )

    max_number_of_fields_to_profile: Optional[int] = Field(
        default=None,
        description="Maximum number of fields to profile per table",
        ge=1
    )

    profile_sample_percentage: float = Field(
        default=100.0,
        description="Percentage of data to sample for profiling",
        ge=0.1,
        le=100.0
    )

    profile_sample_size: Optional[int] = Field(
        default=None,
        description="Maximum number of rows to sample for profiling",
        ge=1000
    )

    include_field_null_count: bool = Field(
        default=True,
        description="Whether to include null count statistics"
    )

    include_field_min_max: bool = Field(
        default=True,
        description="Whether to include min/max value statistics"
    )

    include_field_mean_stddev: bool = Field(
        default=True,
        description="Whether to include mean and standard deviation statistics"
    )

    include_field_histogram: bool = Field(
        default=False,
        description="Whether to include histogram statistics"
    )

    def get_profiling_config(self) -> Dict[str, Any]:
        """Get profiling configuration as dictionary."""
        return {
            "enabled": self.profiling_enabled,
            "table_level_only": self.profile_table_level_only,
            "max_fields": self.max_number_of_fields_to_profile,
            "sample_percentage": self.profile_sample_percentage,
            "sample_size": self.profile_sample_size,
            "include_null_count": self.include_field_null_count,
            "include_min_max": self.include_field_min_max,
            "include_mean_stddev": self.include_field_mean_stddev,
            "include_histogram": self.include_field_histogram
        }


class LineageConfigMixin(ConfigModel):
    """
    Mixin for lineage extraction configuration.

    Provides configuration for data lineage tracking and relationship
    extraction between datasets.
    """

    include_lineage: bool = Field(
        default=True,
        description="Whether to extract lineage information"
    )

    include_column_lineage: bool = Field(
        default=True,
        description="Whether to extract column-level lineage"
    )

    lineage_extraction_timeout: int = Field(
        default=900,
        description="Timeout for lineage extraction in seconds",
        ge=60,
        le=3600
    )

    max_lineage_depth: int = Field(
        default=10,
        description="Maximum depth for lineage traversal",
        ge=1,
        le=50
    )

    include_view_lineage: bool = Field(
        default=True,
        description="Whether to include view-to-table lineage"
    )

    @validator("include_column_lineage")
    def validate_column_lineage_dependency(cls, v, values):
        """Validate that column lineage requires table lineage."""
        if v and not values.get("include_lineage", True):
            raise ValueError("include_lineage must be True when include_column_lineage is True")
        return v


# Combined configuration class using all mixins
class SourceCommonConfig(
    EnvConfigMixin,
    PlatformInstanceConfigMixin,
    LowerCaseDatasetUrnConfigMixin,
    DatasetFilterMixin,
    ConnectionConfigMixin,
    StatefulIngestionMixin,
    ProfilingConfigMixin,
    LineageConfigMixin
):
    """
    Comprehensive source configuration combining all common mixins.

    This class can be used as a base for data source configurations
    that need most of the common functionality.
    """

    source_name: str = Field(
        description="Human-readable name for this data source"
    )

    source_type: str = Field(
        description="Type identifier for this data source"
    )

    description: Optional[str] = Field(
        default=None,
        description="Optional description of this data source"
    )

    tags: List[str] = Field(
        default_factory=list,
        description="List of tags to apply to this source"
    )

    @root_validator
    def validate_source_config(cls, values):
        """Validate overall source configuration."""
        # Ensure source name and type are provided
        if not values.get("source_name"):
            raise ValueError("source_name is required")
        if not values.get("source_type"):
            raise ValueError("source_type is required")

        return values

    def get_source_identifier(self) -> str:
        """Get unique identifier for this source."""
        identifier = f"{self.source_type}.{self.source_name}"
        if self.platform_instance:
            identifier = f"{identifier}.{self.platform_instance}"
        return identifier.lower()
