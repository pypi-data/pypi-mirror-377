"""
DataGuild Connection Resolver

Automatic connection parameter resolution for various data sources
with environment variable substitution, credential management, and
multi-platform support.
"""

import os
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from .common import MetaError, ConfigModel

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    """Supported connection types."""
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    POSTGRES = "postgres"
    MYSQL = "mysql"
    REDSHIFT = "redshift"
    DATABRICKS = "databricks"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"
    UNKNOWN = "unknown"


@dataclass
class ConnectionParams:
    """Standardized connection parameters."""
    connection_type: ConnectionType
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    warehouse: Optional[str] = None
    role: Optional[str] = None
    account: Optional[str] = None
    region: Optional[str] = None
    project_id: Optional[str] = None
    auth_method: Optional[str] = None
    ssl_mode: Optional[str] = None
    additional_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {}
        for key, value in self.__dict__.items():
            if value is not None and key != 'additional_params':
                result[key.replace('_', '')] = value

        # Add additional params
        if self.additional_params:
            result.update(self.additional_params)

        return result

    def get_connection_url(self) -> Optional[str]:
        """Generate connection URL based on connection type."""
        if self.connection_type == ConnectionType.SNOWFLAKE:
            return f"snowflake://{self.username}:{self.password}@{self.account}/{self.database}/{self.schema}?warehouse={self.warehouse}&role={self.role}"
        elif self.connection_type == ConnectionType.POSTGRES:
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.connection_type == ConnectionType.MYSQL:
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.connection_type == ConnectionType.REDSHIFT:
            return f"redshift://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

        return None


class ConnectionResolver:
    """Advanced connection parameter resolver."""

    def __init__(self, env_prefix: str = "DATAGUILD_"):
        self.env_prefix = env_prefix
        self._resolvers: Dict[ConnectionType, Callable] = {
            ConnectionType.SNOWFLAKE: self._resolve_snowflake,
            ConnectionType.BIGQUERY: self._resolve_bigquery,
            ConnectionType.POSTGRES: self._resolve_postgres,
            ConnectionType.MYSQL: self._resolve_mysql,
            ConnectionType.REDSHIFT: self._resolve_redshift,
            ConnectionType.DATABRICKS: self._resolve_databricks,
        }

    def resolve(self, config: Union[Dict[str, Any], str]) -> ConnectionParams:
        """
        Resolve connection parameters from config or connection string.

        Args:
            config: Configuration dictionary or connection string

        Returns:
            ConnectionParams object with resolved parameters

        Raises:
            MetaError: If connection resolution fails
        """
        try:
            if isinstance(config, str):
                return self._resolve_from_url(config)
            elif isinstance(config, dict):
                return self._resolve_from_dict(config)
            else:
                raise MetaError(f"Invalid config type: {type(config)}", code=2001)

        except Exception as e:
            if isinstance(e, MetaError):
                raise
            raise MetaError(f"Connection resolution failed: {e}", code=2002)

    def _resolve_from_url(self, url: str) -> ConnectionParams:
        """Resolve connection from URL string."""
        parsed = urlparse(url)
        connection_type = self._detect_connection_type_from_scheme(parsed.scheme)

        params = ConnectionParams(
            connection_type=connection_type,
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip('/') if parsed.path else None,
            username=parsed.username,
            password=parsed.password
        )

        # Parse query parameters
        if parsed.query:
            query_params = parse_qs(parsed.query)
            for key, values in query_params.items():
                if values:
                    setattr(params, key, values[0])

        return params

    def _resolve_from_dict(self, config: Dict[str, Any]) -> ConnectionParams:
        """Resolve connection from configuration dictionary."""
        # Detect connection type
        connection_type = self._detect_connection_type_from_config(config)

        # Apply environment variable substitution
        resolved_config = self._resolve_environment_variables(config)

        # Use specific resolver
        if connection_type in self._resolvers:
            return self._resolvers[connection_type](resolved_config)
        else:
            return self._resolve_generic(resolved_config, connection_type)

    def _detect_connection_type_from_scheme(self, scheme: str) -> ConnectionType:
        """Detect connection type from URL scheme."""
        scheme_mapping = {
            'snowflake': ConnectionType.SNOWFLAKE,
            'postgresql': ConnectionType.POSTGRES,
            'postgres': ConnectionType.POSTGRES,
            'mysql': ConnectionType.MYSQL,
            'redshift': ConnectionType.REDSHIFT,
            'databricks': ConnectionType.DATABRICKS,
        }
        return scheme_mapping.get(scheme.lower(), ConnectionType.UNKNOWN)

    def _detect_connection_type_from_config(self, config: Dict[str, Any]) -> ConnectionType:
        """Detect connection type from configuration."""
        # Explicit type specification
        if 'type' in config:
            try:
                return ConnectionType(config['type'].lower())
            except ValueError:
                pass

        # Heuristic detection based on config keys
        if 'account' in config and 'warehouse' in config:
            return ConnectionType.SNOWFLAKE
        elif 'project_id' in config or 'project' in config:
            return ConnectionType.BIGQUERY
        elif 'cluster' in config and 'token' in config:
            return ConnectionType.DATABRICKS
        elif 'host' in config:
            port = config.get('port', 5432)
            if port in [5432, 5433]:
                return ConnectionType.POSTGRES
            elif port in [3306]:
                return ConnectionType.MYSQL
            elif port in [5439]:
                return ConnectionType.REDSHIFT

        return ConnectionType.UNKNOWN

    def _resolve_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve environment variables in configuration values."""
        resolved = {}

        for key, value in config.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                # Environment variable substitution: ${VAR_NAME} or ${VAR_NAME:default}
                var_expr = value[2:-1]
                if ':' in var_expr:
                    var_name, default_value = var_expr.split(':', 1)
                else:
                    var_name, default_value = var_expr, None

                # Try with prefix first, then without
                env_value = (
                        os.getenv(f"{self.env_prefix}{var_name}") or
                        os.getenv(var_name) or
                        default_value
                )

                if env_value is None:
                    raise MetaError(f"Environment variable not found: {var_name}", code=2003)

                resolved[key] = env_value
            else:
                resolved[key] = value

        return resolved

    def _resolve_snowflake(self, config: Dict[str, Any]) -> ConnectionParams:
        """Resolve Snowflake connection parameters."""
        return ConnectionParams(
            connection_type=ConnectionType.SNOWFLAKE,
            account=config.get('account'),
            username=config.get('user', config.get('username')),
            password=config.get('password'),
            warehouse=config.get('warehouse'),
            database=config.get('database'),
            schema=config.get('schema'),
            role=config.get('role'),
            region=config.get('region'),
            auth_method=config.get('auth_method', 'password'),
            additional_params={
                'application': config.get('application', 'DataGuild'),
                'client_session_keep_alive': config.get('client_session_keep_alive', True),
                'login_timeout': config.get('login_timeout', 60),
                'network_timeout': config.get('network_timeout', 300),
            }
        )

    def _resolve_bigquery(self, config: Dict[str, Any]) -> ConnectionParams:
        """Resolve BigQuery connection parameters."""
        return ConnectionParams(
            connection_type=ConnectionType.BIGQUERY,
            project_id=config.get('project_id', config.get('project')),
            auth_method=config.get('auth_method', 'service_account'),
            additional_params={
                'credentials_path': config.get('credentials_path'),
                'location': config.get('location', 'US'),
                'maximum_bytes_billed': config.get('maximum_bytes_billed'),
            }
        )

    def _resolve_postgres(self, config: Dict[str, Any]) -> ConnectionParams:
        """Resolve PostgreSQL connection parameters."""
        return ConnectionParams(
            connection_type=ConnectionType.POSTGRES,
            host=config.get('host', 'localhost'),
            port=config.get('port', 5432),
            database=config.get('database'),
            schema=config.get('schema', 'public'),
            username=config.get('user', config.get('username')),
            password=config.get('password'),
            ssl_mode=config.get('ssl_mode', 'prefer'),
            additional_params={
                'connect_timeout': config.get('connect_timeout', 10),
                'application_name': config.get('application_name', 'DataGuild'),
            }
        )

    def _resolve_mysql(self, config: Dict[str, Any]) -> ConnectionParams:
        """Resolve MySQL connection parameters."""
        return ConnectionParams(
            connection_type=ConnectionType.MYSQL,
            host=config.get('host', 'localhost'),
            port=config.get('port', 3306),
            database=config.get('database'),
            username=config.get('user', config.get('username')),
            password=config.get('password'),
            additional_params={
                'charset': config.get('charset', 'utf8mb4'),
                'connect_timeout': config.get('connect_timeout', 10),
            }
        )

    def _resolve_redshift(self, config: Dict[str, Any]) -> ConnectionParams:
        """Resolve Redshift connection parameters."""
        return ConnectionParams(
            connection_type=ConnectionType.REDSHIFT,
            host=config.get('host'),
            port=config.get('port', 5439),
            database=config.get('database'),
            schema=config.get('schema', 'public'),
            username=config.get('user', config.get('username')),
            password=config.get('password'),
            additional_params={
                'ssl': config.get('ssl', True),
                'connect_timeout': config.get('connect_timeout', 10),
            }
        )

    def _resolve_databricks(self, config: Dict[str, Any]) -> ConnectionParams:
        """Resolve Databricks connection parameters."""
        return ConnectionParams(
            connection_type=ConnectionType.DATABRICKS,
            host=config.get('host'),
            username=config.get('username', 'token'),
            password=config.get('token', config.get('password')),
            additional_params={
                'cluster_id': config.get('cluster_id'),
                'http_path': config.get('http_path'),
                'catalog': config.get('catalog', 'hive_metastore'),
                'schema': config.get('schema', 'default'),
            }
        )

    def _resolve_generic(self, config: Dict[str, Any], connection_type: ConnectionType) -> ConnectionParams:
        """Generic connection parameter resolution."""
        return ConnectionParams(
            connection_type=connection_type,
            host=config.get('host'),
            port=config.get('port'),
            database=config.get('database'),
            schema=config.get('schema'),
            username=config.get('user', config.get('username')),
            password=config.get('password'),
            additional_params=config
        )


# Global resolver instance
_default_resolver = ConnectionResolver()


def auto_connection_resolver(config: Union[Dict[str, Any], str]) -> ConnectionParams:
    """
    Automatically resolve connection parameters from configuration.

    Args:
        config: Configuration dictionary or connection string

    Returns:
        ConnectionParams object with resolved connection parameters

    Example:
        >>> config = {
        ...     "account": "myaccount",
        ...     "user": "myuser",
        ...     "password": "${SNOWFLAKE_PASSWORD}",
        ...     "warehouse": "COMPUTE_WH",
        ...     "database": "MY_DB"
        ... }
        >>> params = auto_connection_resolver(config)
        >>> print(params.connection_type)  # ConnectionType.SNOWFLAKE
    """
    return _default_resolver.resolve(config)


def create_connection_resolver(env_prefix: str = "DATAGUILD_") -> ConnectionResolver:
    """
    Create a custom connection resolver with specific environment prefix.

    Args:
        env_prefix: Prefix for environment variable lookup

    Returns:
        ConnectionResolver instance
    """
    return ConnectionResolver(env_prefix=env_prefix)


def validate_connection(params: ConnectionParams) -> List[str]:
    """
    Validate connection parameters for completeness.

    Args:
        params: Connection parameters to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if params.connection_type == ConnectionType.SNOWFLAKE:
        required_fields = ['account', 'username', 'password', 'warehouse']
        for field in required_fields:
            if not getattr(params, field):
                errors.append(f"Snowflake connection missing required field: {field}")

    elif params.connection_type == ConnectionType.BIGQUERY:
        if not params.project_id:
            errors.append("BigQuery connection missing required field: project_id")

    elif params.connection_type in [ConnectionType.POSTGRES, ConnectionType.MYSQL]:
        required_fields = ['host', 'database', 'username']
        for field in required_fields:
            if not getattr(params, field):
                errors.append(f"{params.connection_type.value} connection missing required field: {field}")

    return errors


def get_supported_connection_types() -> List[ConnectionType]:
    """Get list of supported connection types."""
    return [ct for ct in ConnectionType if ct != ConnectionType.UNKNOWN]


# Convenience functions for specific connection types
def resolve_snowflake_connection(config: Dict[str, Any]) -> ConnectionParams:
    """Resolve Snowflake connection specifically."""
    config['type'] = 'snowflake'
    return auto_connection_resolver(config)


def resolve_bigquery_connection(config: Dict[str, Any]) -> ConnectionParams:
    """Resolve BigQuery connection specifically."""
    config['type'] = 'bigquery'
    return auto_connection_resolver(config)


def resolve_postgres_connection(config: Dict[str, Any]) -> ConnectionParams:
    """Resolve PostgreSQL connection specifically."""
    config['type'] = 'postgres'
    return auto_connection_resolver(config)
