"""
MCP Resources for SQL Server MCP Server.

This module implements MCP resources for status monitoring
and query history tracking.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
import structlog

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel
)

from ..models.connection import ConnectionStatus
from ..models.query import QueryHistory, QueryStatistics
from ..services.connection_manager import ConnectionManager
from ..services.query_executor import QueryExecutor


logger = structlog.get_logger(__name__)


class StatusResource:
    """MCP resource for connection status monitoring."""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize the status resource."""
        self.connection_manager = connection_manager
    
    def get_resource_definition(self) -> Resource:
        """Get the resource definition for MCP."""
        return Resource(
            uri="sqlserver://status",
            name="Connection Status",
            description="Current status of all database connections",
            mimeType="application/json"
        )
    
    async def get_content(self) -> str:
        """Get the current status content."""
        try:
            # Get all connection statuses
            connections = await self.connection_manager.list_connections()
            
            # Format status data
            status_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_connections": len(connections),
                "connections": []
            }
            
            for conn_status in connections:
                # Get health information
                health = await self.connection_manager.get_connection_health(conn_status.connection_id)
                
                connection_info = {
                    "connection_id": conn_status.connection_id,
                    "server": conn_status.server,
                    "database": conn_status.database,
                    "connected": conn_status.connected,
                    "authentication_method": conn_status.authentication_method,
                    "last_activity": conn_status.last_activity.isoformat(),
                    "pool_status": conn_status.pool_status,
                    "response_time_ms": conn_status.response_time_ms,
                    "uptime_seconds": conn_status.uptime_seconds,
                    "error_count": conn_status.error_count,
                    "last_error": conn_status.last_error,
                    "health": {
                        "response_time_ms": health.response_time_ms if health else 0.0,
                        "error_count": health.error_count if health else 0,
                        "uptime_seconds": health.uptime_seconds if health else 0.0,
                        "is_healthy": health.is_healthy() if health else False
                    }
                }
                status_data["connections"].append(connection_info)
            
            return json.dumps(status_data, indent=2)
            
        except Exception as e:
            logger.error("Failed to get status resource", error=str(e))
            error_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "total_connections": 0,
                "connections": []
            }
            return json.dumps(error_data, indent=2)


class HistoryResource:
    """MCP resource for query history tracking."""
    
    def __init__(self, query_executor: QueryExecutor):
        """Initialize the history resource."""
        self.query_executor = query_executor
    
    def get_resource_definition(self) -> Resource:
        """Get the resource definition for MCP."""
        return Resource(
            uri="sqlserver://history",
            name="Query History",
            description="History of executed SQL queries",
            mimeType="application/json"
        )
    
    async def get_content(self, limit: int = 100) -> str:
        """Get the query history content."""
        try:
            # Get query history
            history = await self.query_executor.get_query_history(limit=limit)
            
            # Get statistics
            stats = await self.query_executor.get_query_statistics()
            
            # Format history data
            history_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_queries": len(history),
                "statistics": stats.to_dict(),
                "queries": []
            }
            
            for query in history:
                query_info = {
                    "query_id": query.query_id,
                    "query": query.query,
                    "database": query.database,
                    "execution_time_ms": query.execution_time_ms,
                    "row_count": query.row_count,
                    "status": query.status,
                    "error_message": query.error_message,
                    "timestamp": query.timestamp.isoformat(),
                    "parameters": [param.dict() for param in query.parameters]
                }
                history_data["queries"].append(query_info)
            
            return json.dumps(history_data, indent=2)
            
        except Exception as e:
            logger.error("Failed to get history resource", error=str(e))
            error_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "total_queries": 0,
                "statistics": {},
                "queries": []
            }
            return json.dumps(error_data, indent=2)


class PerformanceResource:
    """MCP resource for performance monitoring."""
    
    def __init__(self, query_executor: QueryExecutor):
        """Initialize the performance resource."""
        self.query_executor = query_executor
    
    def get_resource_definition(self) -> Resource:
        """Get the resource definition for MCP."""
        return Resource(
            uri="sqlserver://performance",
            name="Performance Metrics",
            description="Query performance statistics and metrics",
            mimeType="application/json"
        )
    
    async def get_content(self) -> str:
        """Get the performance metrics content."""
        try:
            # Get performance statistics
            perf_stats = await self.query_executor.get_query_performance_stats()
            
            # Get general statistics
            stats = await self.query_executor.get_query_statistics()
            
            # Format performance data
            performance_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "query_statistics": stats.to_dict(),
                "performance_metrics": perf_stats,
                "recommendations": self._generate_recommendations(perf_stats, stats)
            }
            
            return json.dumps(performance_data, indent=2)
            
        except Exception as e:
            logger.error("Failed to get performance resource", error=str(e))
            error_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "query_statistics": {},
                "performance_metrics": {},
                "recommendations": []
            }
            return json.dumps(error_data, indent=2)
    
    def _generate_recommendations(self, perf_stats: Dict[str, Any], stats) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # Check average execution time
        if stats.average_execution_time_ms > 1000:
            recommendations.append("Average query execution time is high (>1s). Consider optimizing queries.")
        
        # Check success rate
        success_rate = stats.calculate_success_rate()
        if success_rate < 95:
            recommendations.append(f"Query success rate is low ({success_rate:.1f}%). Check for connection issues.")
        
        # Check for slow queries
        if perf_stats.get("slowest_query", {}).get("execution_time_ms", 0) > 5000:
            recommendations.append("Some queries are taking >5s to execute. Consider query optimization.")
        
        # Check total queries
        if stats.total_queries > 1000:
            recommendations.append("High query volume detected. Consider connection pooling optimization.")
        
        if not recommendations:
            recommendations.append("Performance metrics look good!")
        
        return recommendations


# Global resource instances
_status_resource = None
_history_resource = None
_performance_resource = None


def get_status_resource() -> StatusResource:
    """Get the global status resource instance."""
    global _status_resource
    if _status_resource is None:
        raise RuntimeError("Status resource not initialized")
    return _status_resource


def get_history_resource() -> HistoryResource:
    """Get the global history resource instance."""
    global _history_resource
    if _history_resource is None:
        raise RuntimeError("History resource not initialized")
    return _history_resource


def get_performance_resource() -> PerformanceResource:
    """Get the global performance resource instance."""
    global _performance_resource
    if _performance_resource is None:
        raise RuntimeError("Performance resource not initialized")
    return _performance_resource


def initialize_resources(
    connection_manager: ConnectionManager,
    query_executor: QueryExecutor
) -> None:
    """Initialize all MCP resources."""
    global _status_resource, _history_resource, _performance_resource
    
    _status_resource = StatusResource(connection_manager)
    _history_resource = HistoryResource(query_executor)
    _performance_resource = PerformanceResource(query_executor)
    
    logger.info("MCP resources initialized")