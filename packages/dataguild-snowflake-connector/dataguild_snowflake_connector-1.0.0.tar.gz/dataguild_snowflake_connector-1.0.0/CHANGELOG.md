# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial release of DataGuild Snowflake Connector
- Complete metadata extraction for Snowflake data warehouses
- Advanced lineage tracking with table-to-table and column-level lineage
- Comprehensive usage analytics and operational metrics
- Data governance support with tag extraction and classification
- Production-ready error handling and monitoring
- Scalable architecture optimized for enterprise deployments
- Support for Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Command-line interface for easy integration
- Comprehensive test suite with unit and integration tests
- Detailed documentation and examples

### Features
- **Metadata Extraction**: Tables, views, streams, procedures, functions, and more
- **Lineage Tracking**: Complete data lineage with SQL parsing and dependency analysis
- **Usage Analytics**: Query performance metrics and resource utilization
- **Data Governance**: Tag management and data classification
- **Monitoring**: Prometheus metrics and structured logging
- **Configuration**: Flexible YAML-based configuration system
- **CLI Tools**: Easy-to-use command-line interface

### Dependencies
- pydantic>=1.10.0,<2.0.0
- snowflake-connector-python>=3.0.0
- sqlparse>=0.4.0
- PyYAML>=6.0
- click>=8.0.0
- typing-extensions>=4.0.0
- sqlalchemy>=1.4.0
- pandas>=1.3.0
- structlog>=22.0.0
- psutil>=5.8.0
- snowflake-sqlalchemy>=1.4.0
- prometheus-client>=0.15.0

### Installation
```bash
pip install dataguild-snowflake-connector
```

### Usage
```python
from dataguild_snowflake_connector import SnowflakeV2Source, SnowflakeV2Config

# Configure your Snowflake connection
config = SnowflakeV2Config(
    account="your-account",
    user="your-user",
    password="your-password",
    warehouse="your-warehouse",
    database="your-database"
)

# Create and run the source
source = SnowflakeV2Source(config)
source.run()
```

### CLI Usage
```bash
dataguild-snowflake --config config.yml --output output.json
```
