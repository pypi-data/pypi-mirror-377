# DataGuild Snowflake Connector

[![PyPI version](https://badge.fury.io/py/dataguild-snowflake-connector.svg)](https://badge.fury.io/py/dataguild-snowflake-connector)
[![Python Support](https://img.shields.io/pypi/pyversions/dataguild-snowflake-connector.svg)](https://pypi.org/project/dataguild-snowflake-connector/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Downloads](https://pepy.tech/badge/dataguild-snowflake-connector)](https://pepy.tech/project/dataguild-snowflake-connector)

Enterprise-grade Snowflake metadata ingestion connector for DataGuild platform with comprehensive lineage tracking, usage analytics, and data governance capabilities.

## 🚀 Features

- **Complete Metadata Extraction**: Tables, views, streams, procedures, functions, and more
- **Advanced Lineage Tracking**: Table-to-table and column-level lineage with SQL parsing
- **Usage Analytics**: Comprehensive usage statistics and operational metrics  
- **Data Governance**: Tag extraction and classification support
- **Production Ready**: Enhanced error handling, monitoring, and structured logging
- **Scalable**: Optimized for enterprise-scale Snowflake deployments
- **CLI Support**: Easy-to-use command-line interface
- **Flexible Configuration**: YAML-based configuration system

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install dataguild-snowflake-connector
```

### From Source

```bash
git clone https://github.com/dataguild/snowflake-connector.git
cd snowflake-connector
pip install -e .
```

## 🚀 Quick Start

### Basic Usage

```python
from dataguild_snowflake_connector import SnowflakeV2Source, SnowflakeV2Config

# Configure your Snowflake connection
config = SnowflakeV2Config(
    account="your-account.snowflakecomputing.com",
    user="your-username",
    password="your-password",
    warehouse="your-warehouse",
    database="your-database",
    schema="your-schema"
)

# Create and run the source
source = SnowflakeV2Source(config)
source.run()
```

### Command Line Interface

```bash
# Basic usage
dataguild-snowflake --config config.yml --output metadata.json

# With specific options
dataguild-snowflake \
  --account your-account \
  --user your-username \
  --password your-password \
  --warehouse your-warehouse \
  --database your-database \
  --output metadata.json
```

### Configuration File

Create a `config.yml` file:

```yaml
account: "your-account.snowflakecomputing.com"
user: "your-username"
password: "your-password"
warehouse: "your-warehouse"
database: "your-database"
schema: "your-schema"

# Optional settings
include_usage_stats: true
include_lineage: true
include_tags: true
max_workers: 4
```

## 📚 Documentation

### API Reference

#### SnowflakeV2Config

Configuration class for Snowflake connection parameters.

```python
class SnowflakeV2Config:
    account: str
    user: str
    password: str
    warehouse: str
    database: str
    schema: Optional[str] = None
    include_usage_stats: bool = True
    include_lineage: bool = True
    include_tags: bool = True
    max_workers: int = 4
```

#### SnowflakeV2Source

Main source class for metadata extraction.

```python
class SnowflakeV2Source:
    def __init__(self, config: SnowflakeV2Config)
    def run(self) -> Dict[str, Any]
    def extract_metadata(self) -> Dict[str, Any]
    def extract_lineage(self) -> Dict[str, Any]
    def extract_usage_stats(self) -> Dict[str, Any]
```

### Advanced Usage

#### Custom Configuration

```python
from dataguild_snowflake_connector import SnowflakeV2Source, SnowflakeV2Config

config = SnowflakeV2Config(
    account="your-account",
    user="your-user",
    password="your-password",
    warehouse="your-warehouse",
    database="your-database",
    # Advanced options
    include_usage_stats=True,
    include_lineage=True,
    include_tags=True,
    max_workers=8,
    connection_timeout=300,
    query_timeout=600
)

source = SnowflakeV2Source(config)
metadata = source.run()
```

#### Error Handling

```python
from dataguild_snowflake_connector import SnowflakeV2Source, SnowflakeV2Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    config = SnowflakeV2Config(...)
    source = SnowflakeV2Source(config)
    metadata = source.run()
    print(f"Successfully extracted metadata for {len(metadata.get('tables', []))} tables")
except Exception as e:
    logging.error(f"Failed to extract metadata: {e}")
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=dataguild

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

## 📊 Output Format

The connector outputs structured metadata in JSON format:

```json
{
  "tables": [...],
  "views": [...],
  "procedures": [...],
  "functions": [...],
  "lineage": [...],
  "usage_stats": [...],
  "tags": [...],
  "extraction_summary": {
    "total_objects": 150,
    "extraction_time": "2024-01-01T12:00:00Z",
    "duration_seconds": 45.2
  }
}
```

## 🔧 Development

### Setup Development Environment

```bash
git clone https://github.com/dataguild/snowflake-connector.git
cd snowflake-connector
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black dataguild/

# Sort imports
isort dataguild/

# Lint code
flake8 dataguild/

# Type checking
mypy dataguild/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://dataguild-snowflake.readthedocs.io](https://dataguild-snowflake.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/dataguild/snowflake-connector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dataguild/snowflake-connector/discussions)

## 🗺️ Roadmap

- [ ] Support for additional Snowflake object types
- [ ] Enhanced lineage visualization
- [ ] Real-time metadata streaming
- [ ] Integration with additional data catalogs
- [ ] Advanced data quality metrics

## 📈 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes.

