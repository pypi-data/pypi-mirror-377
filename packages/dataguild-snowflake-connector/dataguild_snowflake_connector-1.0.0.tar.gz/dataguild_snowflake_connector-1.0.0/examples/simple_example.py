#!/usr/bin/env python3
"""
Simple example of using the Snowflake to Neo4j metadata ingestion module.

This example shows the basic usage of the DataGuild Neo4j integration
with minimal configuration.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dataguild.source.snowflake.config import SnowflakeV2Config
from dataguild.neo4j.connection import Neo4jConnectionConfig
from dataguild.neo4j.config import Neo4jConfig, PipelineConfig
from dataguild.neo4j.orchestrator import run_metadata_ingestion


def main():
    """Simple example of metadata ingestion."""
    
    # Configure Snowflake connection
    snowflake_config = SnowflakeV2Config(
        account_identifier="your-account-identifier",
        username="your-username",
        password=os.getenv("SNOWFLAKE_PASSWORD", "your-password"),
        warehouse="COMPUTE_WH",
        role="ACCOUNTADMIN",
        database="ANALYTICS",
        schema="PUBLIC",
        
        # Basic settings for faster extraction
        include_table_lineage=True,
        include_column_lineage=False,
        include_usage_stats=False,
        include_technical_schema=True,
        include_view_definitions=True,
        
        # Simple filtering
        database_pattern={
            "allow": ["ANALYTICS.*"],
            "deny": [".*_TEST$", ".*_TEMP$"]
        },
        
        # Performance settings
        use_queries_v2=True,
        lazy_schema_resolver=True
    )
    
    # Configure Neo4j connection
    neo4j_config = Neo4jConnectionConfig(
        uri="bolt://localhost:7687",
        username="neo4j",
        password=os.getenv("NEO4J_PASSWORD", "your-password"),
        database="neo4j"
    )
    
    # Create main pipeline configuration
    config = Neo4jConfig(
        snowflake=snowflake_config,
        neo4j=neo4j_config,
        batch_size=500,  # Smaller batch size for example
        clear_existing_metadata=True,  # Clear existing data
        enable_verification=True,
        log_level="INFO"
    )
    
    # Create pipeline runtime configuration
    pipeline_config = PipelineConfig(
        dry_run=False,  # Set to True for testing
        verbose=True
    )
    
    print("Starting simple metadata ingestion example...")
    print(f"Snowflake: {snowflake_config.account_identifier}")
    print(f"Neo4j: {neo4j_config.uri}")
    print()
    
    try:
        # Run the pipeline
        results = run_metadata_ingestion(config, pipeline_config)
        
        if results['success']:
            print("✅ Metadata ingestion completed successfully!")
            
            # Print basic statistics
            if 'graph_statistics' in results:
                stats = results['graph_statistics']
                print(f"📊 Ingested {stats.get('total_nodes', 0)} nodes and {stats.get('total_relationships', 0)} relationships")
                
                # Show node breakdown
                node_counts = stats.get('node_counts', {})
                for node_type, count in node_counts.items():
                    if count > 0:
                        print(f"   - {node_type}: {count}")
            
            print(f"⏱️  Total time: {results['pipeline_duration_seconds']:.2f} seconds")
            
        else:
            print("❌ Metadata ingestion failed!")
            if 'error' in results:
                print(f"Error: {results['error']}")
    
    except Exception as e:
        print(f"❌ Error running pipeline: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
