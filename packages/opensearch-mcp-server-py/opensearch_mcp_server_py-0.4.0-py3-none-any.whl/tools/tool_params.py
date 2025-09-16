# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field
from typing import Any, Optional


class baseToolArgs(BaseModel):
    """Base class for all tool arguments that contains common OpenSearch connection parameters."""

    opensearch_cluster_name: str = Field(
        default='', description='The name of the OpenSearch cluster'
    )


class ListIndicesArgs(baseToolArgs):
    index: str = Field(
        default='',
        description='The name of the index to get detailed information for. If provided, returns detailed information about this specific index instead of listing all indices.',
    )
    include_detail: bool = Field(
        default=True,
        description='Whether to include detailed information. When listing indices (no index specified), if False, returns only a pure list of index names. If True, returns full metadata. When a specific index is provided, detailed information (including mappings) will be returned.',
    )


class GetIndexMappingArgs(baseToolArgs):
    index: str = Field(description='The name of the index to get mapping information for')


class SearchIndexArgs(baseToolArgs):
    index: str = Field(description='The name of the index to search in')
    query: Any = Field(description='The search query in OpenSearch query DSL format')


class GetShardsArgs(baseToolArgs):
    index: str = Field(description='The name of the index to get shard information for')


class GetClusterStateArgs(baseToolArgs):
    """Arguments for the GetClusterStateTool."""
    
    metric: Optional[str] = Field(
        default=None, 
        description='Limit the information returned to the specified metrics. Options include: _all, blocks, metadata, nodes, routing_table, routing_nodes, master_node, version'
    )
    index: Optional[str] = Field(
        default=None, 
        description='Limit the information returned to the specified indices'
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "metric": "nodes",
                    "index": "my_index"
                },
                {
                    "metric": "_all"
                }
            ]
        }


class GetSegmentsArgs(baseToolArgs):
    """Arguments for the GetSegmentsTool."""
    
    index: Optional[str] = Field(
        default=None, 
        description='Limit the information returned to the specified indices. If not provided, returns segments for all indices.'
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "index": "my_index"
                },
                {}  # Empty example to show all segments
            ]
        }


class CatNodesArgs(baseToolArgs):
    """Arguments for the CatNodesTool."""
    
    metrics: Optional[str] = Field(
        default=None, 
        description='A comma-separated list of metrics to display. Available metrics include: id, name, ip, port, role, master, heap.percent, ram.percent, cpu, load_1m, load_5m, load_15m, disk.total, disk.used, disk.avail, disk.used_percent'
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "metrics": "name,ip,heap.percent,cpu,load_1m"
                },
                {}  # Empty example to show all node metrics
            ]
        }


class GetIndexInfoArgs(baseToolArgs):
    """Arguments for the GetIndexInfoTool."""
    
    index: str = Field(
        description='The name of the index to get detailed information for. Wildcards are supported.'
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "index": "my_index"
                },
                {
                    "index": "my_index*"  # Using wildcard
                }
            ]
        }


class GetIndexStatsArgs(baseToolArgs):
    """Arguments for the GetIndexStatsTool."""
    
    index: str = Field(
        description='The name of the index to get statistics for. Wildcards are supported.'
    )
    metric: Optional[str] = Field(
        default=None,
        description='Limit the information returned to the specified metrics. Options include: _all, completion, docs, fielddata, flush, get, indexing, merge, query_cache, refresh, request_cache, search, segments, store, warmer, bulk'
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "index": "my_index"
                },
                {
                    "index": "my_index",
                    "metric": "search,indexing"
                }
            ]
        }


class GetQueryInsightsArgs(baseToolArgs):
    """Arguments for the GetQueryInsightsTool."""
    
    # No additional parameters needed for the basic implementation
    # The tool will simply call GET /_insights/top_queries without parameters
    
    class Config:
        json_schema_extra = {
            "examples": [
                {}  # Empty example as no additional parameters are required
            ]
        }


class GetNodesHotThreadsArgs(baseToolArgs):
    """Arguments for the GetNodesHotThreadsTool."""
    
    # No additional parameters needed for the basic implementation
    # The tool will simply call GET /_nodes/hot_threads without parameters
    
    class Config:
        json_schema_extra = {
            "examples": [
                {}  # Empty example as no additional parameters are required
            ]
        }


class GetAllocationArgs(baseToolArgs):
    """Arguments for the GetAllocationTool."""
    
    # No additional parameters needed for the basic implementation
    # The tool will simply call GET /_cat/allocation without parameters
    
    class Config:
        json_schema_extra = {
            "examples": [
                {}  # Empty example as no additional parameters are required
            ]
        }


class GetLongRunningTasksArgs(baseToolArgs):
    """Arguments for the GetLongRunningTasksTool."""
    
    limit: Optional[int] = Field(
        default=10,
        description='The maximum number of tasks to return. Default is 10.'
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {},  # Default example to show top 10 long-running tasks
                {
                    "limit": 5  # Example to show top 5 long-running tasks
                }
            ]
        }


class GetNodesArgs(baseToolArgs):
    """Arguments for the GetNodesTool."""
    
    node_id: Optional[str] = Field(
        default=None,
        description='A comma-separated list of node IDs or names to limit the returned information. Supports node filters like _local, _master, master:true, data:false, etc. Defaults to _all.'
    )
    metric: Optional[str] = Field(
        default=None,
        description='A comma-separated list of metric groups to include in the response. Options include: settings, os, process, jvm, thread_pool, transport, http, plugins, ingest, aggregations, indices. Defaults to all metrics.'
    )
    
    class Config:
        json_schema_extra = {
            "examples": [
                {},  # Get all nodes with all metrics
                {
                    "node_id": "master:true",
                    "metric": "process,transport"
                },
                {
                    "node_id": "_local",
                    "metric": "jvm,os"
                }
            ]
        }
