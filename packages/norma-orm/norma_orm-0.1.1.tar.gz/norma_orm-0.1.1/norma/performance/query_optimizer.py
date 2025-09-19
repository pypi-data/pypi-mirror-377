"""
Norma Query Optimizer

Provides query optimization and analysis functionality.
"""

import time
import hashlib
from typing import Any, Dict, List, Optional, Type, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter

from ..core.base_model import BaseModel
from ..exceptions import QueryError


@dataclass
class QueryStats:
    """Query execution statistics."""
    
    query_hash: str
    query_type: str  # 'select', 'insert', 'update', 'delete'
    model_name: str
    execution_time: float
    row_count: int
    timestamp: float
    filters: Optional[Dict[str, Any]] = None
    indexes_used: Optional[List[str]] = None


@dataclass 
class QueryOptimization:
    """Query optimization suggestion."""
    
    query_hash: str
    optimization_type: str  # 'index', 'query_rewrite', 'pagination'
    description: str
    impact: str  # 'high', 'medium', 'low'
    implementation: str


class QueryOptimizer:
    """
    Analyzes and optimizes database queries.
    
    Features:
    - Query performance tracking
    - Index recommendations
    - Query pattern analysis
    - Optimization suggestions
    """
    
    def __init__(self, enable_profiling: bool = True):
        """
        Initialize query optimizer.
        
        Args:
            enable_profiling: Whether to enable query profiling
        """
        self.enable_profiling = enable_profiling
        self.query_stats: List[QueryStats] = []
        self.query_patterns: Dict[str, List[QueryStats]] = defaultdict(list)
        self.slow_query_threshold = 1.0  # seconds
        self.optimization_cache: Dict[str, List[QueryOptimization]] = {}
    
    def track_query(
        self,
        model_class: Type[BaseModel],
        query_type: str,
        filters: Optional[Dict[str, Any]] = None,
        execution_time: float = 0.0,
        row_count: int = 0,
        indexes_used: Optional[List[str]] = None
    ) -> str:
        """
        Track query execution for analysis.
        
        Args:
            model_class: Model class being queried
            query_type: Type of query (select, insert, update, delete)
            filters: Query filters used
            execution_time: Query execution time in seconds
            row_count: Number of rows affected/returned
            indexes_used: List of indexes used by the query
            
        Returns:
            Query hash for tracking
        """
        if not self.enable_profiling:
            return ""
        
        # Generate query hash
        query_signature = f"{model_class.__name__}:{query_type}:{str(filters or {})}"
        query_hash = hashlib.md5(query_signature.encode()).hexdigest()
        
        # Create query stats
        stats = QueryStats(
            query_hash=query_hash,
            query_type=query_type,
            model_name=model_class.__name__,
            execution_time=execution_time,
            row_count=row_count,
            timestamp=time.time(),
            filters=filters,
            indexes_used=indexes_used or []
        )
        
        # Store stats
        self.query_stats.append(stats)
        self.query_patterns[query_hash].append(stats)
        
        # Trigger optimization analysis for slow queries
        if execution_time > self.slow_query_threshold:
            self._analyze_slow_query(stats)
        
        return query_hash
    
    def get_slow_queries(self, threshold: Optional[float] = None) -> List[QueryStats]:
        """
        Get queries that exceed the slow query threshold.
        
        Args:
            threshold: Custom threshold in seconds
            
        Returns:
            List of slow query statistics
        """
        threshold = threshold or self.slow_query_threshold
        return [stats for stats in self.query_stats if stats.execution_time > threshold]
    
    def get_query_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze query patterns and frequency.
        
        Returns:
            Dictionary with query pattern analysis
        """
        patterns = {}
        
        for query_hash, stats_list in self.query_patterns.items():
            if not stats_list:
                continue
                
            first_stat = stats_list[0]
            patterns[query_hash] = {
                'model_name': first_stat.model_name,
                'query_type': first_stat.query_type,
                'execution_count': len(stats_list),
                'avg_execution_time': sum(s.execution_time for s in stats_list) / len(stats_list),
                'max_execution_time': max(s.execution_time for s in stats_list),
                'min_execution_time': min(s.execution_time for s in stats_list),
                'avg_row_count': sum(s.row_count for s in stats_list) / len(stats_list),
                'filters_used': self._analyze_filters(stats_list),
                'indexes_used': self._analyze_indexes(stats_list)
            }
        
        return patterns
    
    def get_optimization_suggestions(
        self, 
        model_class: Optional[Type[BaseModel]] = None
    ) -> List[QueryOptimization]:
        """
        Get optimization suggestions for queries.
        
        Args:
            model_class: Specific model to analyze (None for all)
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        patterns = self.get_query_patterns()
        
        for query_hash, pattern in patterns.items():
            # Filter by model if specified
            if model_class and pattern['model_name'] != model_class.__name__:
                continue
            
            # Check if we have cached optimizations
            if query_hash in self.optimization_cache:
                suggestions.extend(self.optimization_cache[query_hash])
                continue
            
            query_suggestions = []
            
            # Analyze for index opportunities
            index_suggestions = self._suggest_indexes(query_hash, pattern)
            query_suggestions.extend(index_suggestions)
            
            # Analyze for query rewrite opportunities
            rewrite_suggestions = self._suggest_query_rewrites(query_hash, pattern)
            query_suggestions.extend(rewrite_suggestions)
            
            # Analyze for pagination opportunities
            pagination_suggestions = self._suggest_pagination(query_hash, pattern)
            query_suggestions.extend(pagination_suggestions)
            
            # Cache suggestions
            self.optimization_cache[query_hash] = query_suggestions
            suggestions.extend(query_suggestions)
        
        return suggestions
    
    def _analyze_slow_query(self, stats: QueryStats):
        """Analyze a slow query for immediate optimization opportunities."""
        # This could trigger immediate analysis and alerts
        pass
    
    def _analyze_filters(self, stats_list: List[QueryStats]) -> Dict[str, int]:
        """Analyze filter patterns in queries."""
        filter_usage = Counter()
        
        for stats in stats_list:
            if stats.filters:
                for field_name in stats.filters.keys():
                    filter_usage[field_name] += 1
        
        return dict(filter_usage)
    
    def _analyze_indexes(self, stats_list: List[QueryStats]) -> Dict[str, int]:
        """Analyze index usage patterns."""
        index_usage = Counter()
        
        for stats in stats_list:
            if stats.indexes_used:
                for index_name in stats.indexes_used:
                    index_usage[index_name] += 1
        
        return dict(index_usage)
    
    def _suggest_indexes(self, query_hash: str, pattern: Dict[str, Any]) -> List[QueryOptimization]:
        """Suggest index optimizations."""
        suggestions = []
        
        # Check for frequently filtered fields without indexes
        filters_used = pattern.get('filters_used', {})
        indexes_used = pattern.get('indexes_used', {})
        
        for field_name, usage_count in filters_used.items():
            # If field is used frequently but no index is used
            if usage_count > 5 and not any(field_name in idx for idx in indexes_used.keys()):
                suggestions.append(QueryOptimization(
                    query_hash=query_hash,
                    optimization_type='index',
                    description=f"Create index on '{field_name}' field for {pattern['model_name']}",
                    impact='high' if usage_count > 20 else 'medium',
                    implementation=f"Add index=True to {field_name} field definition"
                ))
        
        # Check for composite index opportunities
        if len(filters_used) > 1:
            most_used_fields = sorted(filters_used.items(), key=lambda x: x[1], reverse=True)[:3]
            if len(most_used_fields) >= 2:
                field_names = [field for field, _ in most_used_fields]
                suggestions.append(QueryOptimization(
                    query_hash=query_hash,
                    optimization_type='index',
                    description=f"Consider composite index on {', '.join(field_names)} for {pattern['model_name']}",
                    impact='medium',
                    implementation=f"Create database composite index on ({', '.join(field_names)})"
                ))
        
        return suggestions
    
    def _suggest_query_rewrites(self, query_hash: str, pattern: Dict[str, Any]) -> List[QueryOptimization]:
        """Suggest query rewrite optimizations."""
        suggestions = []
        
        # Check for queries that return too many rows
        if pattern['avg_row_count'] > 1000:
            suggestions.append(QueryOptimization(
                query_hash=query_hash,
                optimization_type='query_rewrite',
                description=f"Query returns {pattern['avg_row_count']:.0f} rows on average - consider adding filters",
                impact='high',
                implementation="Add more specific filters or use pagination"
            ))
        
        # Check for N+1 query patterns (would need more sophisticated tracking)
        if pattern['execution_count'] > 100 and pattern['query_type'] == 'select':
            suggestions.append(QueryOptimization(
                query_hash=query_hash,
                optimization_type='query_rewrite',
                description=f"Frequently executed query ({pattern['execution_count']} times) - possible N+1 pattern",
                impact='high',
                implementation="Consider using eager loading or batch queries"
            ))
        
        return suggestions
    
    def _suggest_pagination(self, query_hash: str, pattern: Dict[str, Any]) -> List[QueryOptimization]:
        """Suggest pagination optimizations."""
        suggestions = []
        
        # Suggest pagination for queries returning many rows
        if pattern['avg_row_count'] > 100 and pattern['query_type'] == 'select':
            suggestions.append(QueryOptimization(
                query_hash=query_hash,
                optimization_type='pagination',
                description=f"Query returns {pattern['avg_row_count']:.0f} rows - implement pagination",
                impact='medium',
                implementation="Use limit and offset parameters in find_many() calls"
            ))
        
        return suggestions
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Returns:
            Performance analysis report
        """
        if not self.query_stats:
            return {"message": "No query data available"}
        
        patterns = self.get_query_patterns()
        slow_queries = self.get_slow_queries()
        suggestions = self.get_optimization_suggestions()
        
        # Calculate overall statistics
        total_queries = len(self.query_stats)
        avg_execution_time = sum(s.execution_time for s in self.query_stats) / total_queries
        
        # Model-specific statistics
        model_stats = defaultdict(lambda: {'count': 0, 'total_time': 0.0})
        for stats in self.query_stats:
            model_stats[stats.model_name]['count'] += 1
            model_stats[stats.model_name]['total_time'] += stats.execution_time
        
        # Query type distribution
        query_type_stats = Counter(s.query_type for s in self.query_stats)
        
        return {
            'summary': {
                'total_queries': total_queries,
                'avg_execution_time': avg_execution_time,
                'slow_queries_count': len(slow_queries),
                'unique_query_patterns': len(patterns)
            },
            'model_statistics': {
                model: {
                    'query_count': stats['count'],
                    'avg_execution_time': stats['total_time'] / stats['count']
                }
                for model, stats in model_stats.items()
            },
            'query_type_distribution': dict(query_type_stats),
            'slow_queries': [
                {
                    'model_name': sq.model_name,
                    'query_type': sq.query_type,
                    'execution_time': sq.execution_time,
                    'row_count': sq.row_count,
                    'filters': sq.filters
                }
                for sq in slow_queries[:10]  # Top 10 slowest
            ],
            'optimization_suggestions': [
                {
                    'type': opt.optimization_type,
                    'description': opt.description,
                    'impact': opt.impact,
                    'implementation': opt.implementation
                }
                for opt in suggestions
            ]
        }
    
    def clear_stats(self):
        """Clear all collected statistics."""
        self.query_stats.clear()
        self.query_patterns.clear()
        self.optimization_cache.clear()
