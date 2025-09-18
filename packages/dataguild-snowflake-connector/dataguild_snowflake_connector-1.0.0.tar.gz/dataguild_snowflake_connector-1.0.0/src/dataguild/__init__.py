"""
DataGuild - Enterprise Data Catalog and Governance Platform
"""

__version__ = "1.0.0"
__author__ = "DataGuild Engineering Team"
__email__ = "engineering@dataguild.com"
__license__ = "Apache-2.0"

# Package metadata
__title__ = "dataguild"
__description__ = "Enterprise Data Catalog and Governance Platform"
__url__ = "https://github.com/dataguild/snowflake-connector"

# Version info tuple
__version_info__ = tuple(map(int, __version__.split('.')))

# Make key classes available at package level
try:
    from dataguild.ingestion.source.snowflake.snowflake_v2 import SnowflakeV2Source
    from dataguild.ingestion.source.snowflake.snowflake_config import SnowflakeV2Config

    __all__ = [
        "__version__",
        "__author__",
        "__email__",
        "__license__",
        "SnowflakeV2Source",
        "SnowflakeV2Config"
    ]
except ImportError:
    # If submodules aren't available yet, just export metadata
    __all__ = [
        "__version__",
        "__author__",
        "__email__",
        "__license__"
    ]
