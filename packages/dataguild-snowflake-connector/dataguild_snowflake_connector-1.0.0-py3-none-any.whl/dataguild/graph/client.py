"""
DataGuild Graph Client

This module provides a comprehensive client for querying and interacting
with the DataGuild metadata graph through GraphQL API.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union, Callable, Iterator
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class GraphQLError(Exception):
    """Exception raised when GraphQL queries fail."""

    def __init__(self, message: str, errors: Optional[List[Dict]] = None):
        super().__init__(message)
        self.errors = errors or []


class ConnectionError(Exception):
    """Exception raised when connection to DataGuild fails."""
    pass


class AuthenticationError(Exception):
    """Exception raised when authentication fails."""
    pass


class DataGuildGraphConfig:
    """Configuration class for DataGuild Graph client."""

    def __init__(
            self,
            server: str,
            token: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            timeout: int = 60,
            retry_total: int = 3,
            retry_backoff_factor: float = 0.3,
            max_workers: int = 4,
            cache_ttl: int = 300,  # 5 minutes
            disable_ssl_verification: bool = False
    ):
        """
        Initialize DataGuild Graph configuration.

        Args:
            server: DataGuild server URL
            token: Bearer token for authentication
            username: Username for basic auth (alternative to token)
            password: Password for basic auth (alternative to token)
            timeout: Request timeout in seconds
            retry_total: Total number of retries
            retry_backoff_factor: Backoff factor for retries
            max_workers: Maximum number of concurrent workers
            cache_ttl: Cache time-to-live in seconds
            disable_ssl_verification: Whether to disable SSL verification
        """
        self.server = server.rstrip('/')
        self.token = token
        self.username = username
        self.password = password
        self.timeout = timeout
        self.retry_total = retry_total
        self.retry_backoff_factor = retry_backoff_factor
        self.max_workers = max_workers
        self.cache_ttl = cache_ttl
        self.disable_ssl_verification = disable_ssl_verification

        # Validate configuration
        if not token and not (username and password):
            raise ValueError("Either token or username/password must be provided")


class DataGuildGraph:
    """
    Comprehensive client for DataGuild metadata graph operations.

    Provides GraphQL querying capabilities, entity retrieval, search functionality,
    and batch operations with built-in caching and error handling.
    """

    def __init__(self, config: Union[DataGuildGraphConfig, Dict[str, Any]]):
        """
        Initialize DataGuild Graph client.

        Args:
            config: Configuration object or dictionary
        """
        if isinstance(config, dict):
            config = DataGuildGraphConfig(**config)

        self.config = config
        self._session = self._create_session()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}

        # Test connection on initialization
        self._test_connection()

    def _create_session(self) -> requests.Session:
        """Create configured requests session with retry strategy."""
        session = requests.Session()

        # Configure authentication
        if self.config.token:
            session.headers.update({
                "Authorization": f"Bearer {self.config.token}",
                "Content-Type": "application/json"
            })
        elif self.config.username and self.config.password:
            session.auth = (self.config.username, self.config.password)
            session.headers.update({"Content-Type": "application/json"})

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.retry_total,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=self.config.retry_backoff_factor
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Disable SSL verification if configured
        if self.config.disable_ssl_verification:
            session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        return session

    def _test_connection(self) -> None:
        """Test connection to DataGuild server."""
        try:
            health_url = urljoin(self.config.server, "/health")
            response = self._session.get(health_url, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully connected to DataGuild at {self.config.server}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to DataGuild server: {e}")

    def _get_cache_key(self, query: str, variables: Optional[Dict] = None) -> str:
        """Generate cache key for query."""
        cache_data = {"query": query, "variables": variables or {}}
        return f"query_{hash(json.dumps(cache_data, sort_keys=True))}"

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if not expired."""
        if cache_key not in self._cache:
            return None

        timestamp = self._cache_timestamps.get(cache_key)
        if not timestamp:
            return None

        if datetime.now() - timestamp > timedelta(seconds=self.config.cache_ttl):
            # Cache expired
            del self._cache[cache_key]
            del self._cache_timestamps[cache_key]
            return None

        return self._cache[cache_key]

    def _set_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Set data in cache."""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now()

    def execute_graphql(
            self,
            query: str,
            variables: Optional[Dict[str, Any]] = None,
            use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query against DataGuild.

        Args:
            query: GraphQL query string
            variables: Optional query variables
            use_cache: Whether to use caching

        Returns:
            Query result data

        Raises:
            GraphQLError: If the query fails
            ConnectionError: If connection fails
        """
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(query, variables)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.debug("Returning cached result for GraphQL query")
                return cached_result

        # Prepare request payload
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            # Execute GraphQL request
            graphql_url = urljoin(self.config.server, "/api/graphql")
            response = self._session.post(
                graphql_url,
                json=payload,
                timeout=self.config.timeout
            )

            response.raise_for_status()
            result = response.json()

            # Check for GraphQL errors
            if "errors" in result:
                raise GraphQLError(
                    f"GraphQL query failed: {result['errors']}",
                    errors=result["errors"]
                )

            data = result.get("data", {})

            # Cache the result
            if use_cache:
                self._set_cache(cache_key, data)

            return data

        except requests.exceptions.Timeout:
            raise ConnectionError(f"Request timeout after {self.config.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Failed to connect to DataGuild server")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            else:
                raise ConnectionError(f"HTTP error: {e}")
        except Exception as e:
            raise GraphQLError(f"Unexpected error executing GraphQL query: {e}")

    def get_entity(self, urn: str, aspects: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get a single entity by URN.

        Args:
            urn: Entity URN
            aspects: Optional list of aspects to retrieve

        Returns:
            Entity data or None if not found
        """
        aspects_fragment = ""
        if aspects:
            aspects_fragment = "\n".join([f"... on {aspect} {{ ... }}" for aspect in aspects])

        query = f"""
        query getEntity($urn: String!) {{
            entity(urn: $urn) {{
                urn
                type
                {aspects_fragment}
                ... on Dataset {{
                    name
                    description
                    platform {{
                        name
                        urn
                    }}
                    origin {{
                        type
                        name
                    }}
                    properties {{
                        name
                        description
                        qualifiedName
                        customProperties {{
                            key
                            value
                        }}
                    }}
                    schemaMetadata {{
                        schemaName
                        platform
                        version
                        fields {{
                            fieldPath
                            type
                            nativeDataType
                            description
                            nullable
                            recursive
                        }}
                    }}
                    institutionalMemory {{
                        elements {{
                            url
                            description
                            author {{
                                urn
                                username
                            }}
                        }}
                    }}
                    globalTags {{
                        tags {{
                            tag {{
                                urn
                                name
                            }}
                        }}
                    }}
                }}
                ... on DataJob {{
                    name
                    description
                    properties {{
                        name
                        description
                    }}
                    inputDatasets {{
                        urn
                        name
                    }}
                    outputDatasets {{
                        urn
                        name
                    }}
                }}
                ... on DataFlow {{
                    name
                    description
                    properties {{
                        name
                        description
                    }}
                    jobs {{
                        urn
                        name
                    }}
                }}
            }}
        }}
        """

        variables = {"urn": urn}
        result = self.execute_graphql(query, variables)
        return result.get("entity")

    def get_entities(self, urns: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple entities by URNs in batch.

        Args:
            urns: List of entity URNs

        Returns:
            List of entity data
        """
        if not urns:
            return []

        # For large batches, split into smaller chunks
        chunk_size = 50
        all_entities = []

        for i in range(0, len(urns), chunk_size):
            chunk_urns = urns[i:i + chunk_size]

            query = """
            query getEntities($urns: [String!]!) {
                entities(urns: $urns) {
                    urn
                    type
                    ... on Dataset {
                        name
                        description
                        platform {
                            name
                        }
                        properties {
                            name
                            qualifiedName
                        }
                    }
                }
            }
            """

            variables = {"urns": chunk_urns}
            result = self.execute_graphql(query, variables)
            entities = result.get("entities", [])
            all_entities.extend(entities)

        return all_entities

    def search(
            self,
            query: str,
            entity_types: Optional[List[str]] = None,
            platform: Optional[str] = None,
            start: int = 0,
            count: int = 10,
            facets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for entities in DataGuild.

        Args:
            query: Search query string
            entity_types: Optional list of entity types to filter
            platform: Optional platform filter
            start: Starting offset
            count: Number of results to return
            facets: Optional list of facets to include

        Returns:
            Search results with entities and facets
        """
        search_query = """
        query search(
            $input: SearchInput!
        ) {
            search(input: $input) {
                start
                count
                total
                entities {
                    urn
                    type
                    ... on Dataset {
                        name
                        description
                        platform {
                            name
                        }
                        properties {
                            name
                            qualifiedName
                        }
                    }
                    ... on DataJob {
                        name
                        description
                        properties {
                            name
                        }
                    }
                }
                facets {
                    field
                    displayName
                    aggregations {
                        value
                        count
                    }
                }
            }
        }
        """

        search_input = {
            "type": "KEYWORD",
            "query": query,
            "start": start,
            "count": count
        }

        if entity_types:
            search_input["types"] = entity_types

        if platform:
            search_input["filters"] = [
                {
                    "field": "platform",
                    "value": platform
                }
            ]

        variables = {"input": search_input}
        result = self.execute_graphql(search_query, variables)
        return result.get("search", {})

    def get_lineage(
            self,
            urn: str,
            direction: str = "BOTH",
            max_hops: int = 3
    ) -> Dict[str, Any]:
        """
        Get lineage information for an entity.

        Args:
            urn: Entity URN
            direction: Lineage direction ("UPSTREAM", "DOWNSTREAM", "BOTH")
            max_hops: Maximum number of hops to traverse

        Returns:
            Lineage graph data
        """
        query = """
        query getLineage($urn: String!, $input: LineageInput!) {
            lineage(urn: $urn, input: $input) {
                start
                count
                total
                relationships {
                    type
                    direction
                    entity {
                        urn
                        type
                        ... on Dataset {
                            name
                            platform {
                                name
                            }
                        }
                    }
                    paths {
                        path {
                            urn
                            type
                        }
                    }
                }
            }
        }
        """

        lineage_input = {
            "direction": direction.upper(),
            "maxHops": max_hops,
            "start": 0,
            "count": 100
        }

        variables = {"urn": urn, "input": lineage_input}
        result = self.execute_graphql(query, variables)
        return result.get("lineage", {})

    def get_usage_stats(
            self,
            urn: str,
            range_type: str = "WEEK"
    ) -> Dict[str, Any]:
        """
        Get usage statistics for an entity.

        Args:
            urn: Entity URN
            range_type: Time range ("DAY", "WEEK", "MONTH", "QUARTER", "YEAR")

        Returns:
            Usage statistics data
        """
        query = """
        query getUsageStats($urn: String!, $range: UsageStatsRange!) {
            usageStats(urn: $urn, range: $range) {
                buckets {
                    bucket
                    duration
                    resource
                    metrics {
                        uniqueUserCount
                        totalSqlQueries
                        topSqlQueries
                    }
                    users {
                        user {
                            urn
                            username
                        }
                        count
                        userEmail
                    }
                }
                aggregations {
                    uniqueUserCount
                    totalSqlQueries
                    users {
                        user {
                            urn
                            username
                        }
                        count
                    }
                }
            }
        }
        """

        variables = {"urn": urn, "range": range_type.upper()}
        result = self.execute_graphql(query, variables)
        return result.get("usageStats", {})

    def list_datasets(
            self,
            platform: Optional[str] = None,
            start: int = 0,
            count: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List datasets with optional platform filtering.

        Args:
            platform: Optional platform filter
            start: Starting offset
            count: Number of results to return

        Returns:
            List of dataset entities
        """
        filters = []
        if platform:
            filters.append({
                "field": "platform",
                "value": platform
            })

        search_result = self.search(
            query="*",
            entity_types=["DATASET"],
            start=start,
            count=count
        )

        return search_result.get("entities", [])

    def execute_batch_queries(
            self,
            queries: List[Dict[str, Any]],
            use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple GraphQL queries concurrently.

        Args:
            queries: List of query dictionaries with 'query' and optional 'variables'
            use_cache: Whether to use caching

        Returns:
            List of query results in the same order
        """
        results = [None] * len(queries)

        def execute_single_query(index: int, query_data: Dict[str, Any]) -> None:
            try:
                result = self.execute_graphql(
                    query_data["query"],
                    query_data.get("variables"),
                    use_cache=use_cache
                )
                results[index] = {"success": True, "data": result}
            except Exception as e:
                results[index] = {"success": False, "error": str(e)}

        # Execute queries concurrently
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = [
                executor.submit(execute_single_query, i, query)
                for i, query in enumerate(queries)
            ]

            # Wait for all queries to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Batch query execution failed: {e}")

        return results

    def clear_cache(self) -> None:
        """Clear the query cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Query cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        expired_entries = 0

        now = datetime.now()
        for timestamp in self._cache_timestamps.values():
            if now - timestamp > timedelta(seconds=self.config.cache_ttl):
                expired_entries += 1

        return {
            "total_entries": total_entries,
            "active_entries": total_entries - expired_entries,
            "expired_entries": expired_entries,
            "cache_ttl_seconds": self.config.cache_ttl
        }

    def ping(self) -> Dict[str, Any]:
        """
        Ping DataGuild server to test connectivity.

        Returns:
            Server response with status information
        """
        query = """
        query ping {
            ping {
                status
                timestamp
                version
            }
        }
        """

        try:
            result = self.execute_graphql(query, use_cache=False)
            return result.get("ping", {"status": "ok", "timestamp": datetime.now().isoformat()})
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def close(self) -> None:
        """Close the client session."""
        if self._session:
            self._session.close()
        logger.info("DataGuild Graph client session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"DataGuildGraph(server='{self.config.server}', cache_entries={len(self._cache)})"


# Convenience factory functions
def create_graph_client(
        server: str,
        token: Optional[str] = None,
        **kwargs
) -> DataGuildGraph:
    """
    Create a DataGuildGraph client with token authentication.

    Args:
        server: DataGuild server URL
        token: Authentication token
        **kwargs: Additional configuration options

    Returns:
        Configured DataGuildGraph client
    """
    config = DataGuildGraphConfig(server=server, token=token, **kwargs)
    return DataGuildGraph(config)


def create_graph_client_with_auth(
        server: str,
        username: str,
        password: str,
        **kwargs
) -> DataGuildGraph:
    """
    Create a DataGuildGraph client with username/password authentication.

    Args:
        server: DataGuild server URL
        username: Username for authentication
        password: Password for authentication
        **kwargs: Additional configuration options

    Returns:
        Configured DataGuildGraph client
    """
    config = DataGuildGraphConfig(
        server=server,
        username=username,
        password=password,
        **kwargs
    )
    return DataGuildGraph(config)


# Export all classes and functions
__all__ = [
    'DataGuildGraph',
    'DataGuildGraphConfig',
    'GraphQLError',
    'ConnectionError',
    'AuthenticationError',
    'create_graph_client',
    'create_graph_client_with_auth',
]
