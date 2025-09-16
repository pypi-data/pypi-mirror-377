"""Predefined middleware presets for common use cases."""

from __future__ import annotations

from typing import Optional, Dict, Any
from .middleware import (
    IdempotencyMiddleware, DynamoDBIdempotencyStore, MemoryIdempotencyStore,
    ErrorHandlingMiddleware, RetryConfig, CircuitBreaker,
    VisibilityTimeoutMonitor, ParallelizationMiddleware, ParallelizationConfig,
    LoggingMiddleware, TimingMsMiddleware
)


class MiddlewarePreset:
    """Factory class for creating predefined middleware configurations."""
    @staticmethod
    def production(
        dynamodb_table: Optional[str] = None,
        region_name: Optional[str] = None,
        max_concurrent: int = 10,
        retry_attempts: int = 3,
        visibility_timeout: float = 30.0,
        circuit_breaker_threshold: int = 5
    ) -> list:
        """Create production-ready middleware configuration.
        
        Args:
            dynamodb_table: DynamoDB table name for idempotency
            region_name: AWS region name
            max_concurrent: Maximum concurrent message processing
            retry_attempts: Maximum retry attempts for failed messages
            visibility_timeout: SQS visibility timeout in seconds
            circuit_breaker_threshold: Circuit breaker failure threshold
            
        Returns:
            List of configured middleware instances
        """
        middlewares = []
        
        middlewares.append(LoggingMiddleware(
            verbose=True,
            include_context=True,
            include_record=False
        ))
        middlewares.append(TimingMsMiddleware())
        
        if dynamodb_table:
            store = DynamoDBIdempotencyStore(
                table_name=dynamodb_table,
                region_name=region_name
            )
        else:
            store = MemoryIdempotencyStore()
        
        middlewares.append(IdempotencyMiddleware(
            store=store,
            ttl_seconds=3600
        ))
        
        retry_config = RetryConfig(
            max_retries=retry_attempts,
            base_delay=1.0,
            max_delay=60.0,
            exponential_backoff=True
        )
        circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_threshold,
            recovery_timeout=60.0
        )
        middlewares.append(ErrorHandlingMiddleware(
            retry_config=retry_config,
            circuit_breaker=circuit_breaker
        ))
        
        middlewares.append(VisibilityTimeoutMonitor(
            default_visibility_timeout=visibility_timeout,
            warning_threshold=0.8
        ))
        
        parallel_config = ParallelizationConfig(
            max_concurrent_messages=max_concurrent,
            use_thread_pool=True,
            thread_pool_size=min(32, max_concurrent)
        )
        middlewares.append(ParallelizationMiddleware(config=parallel_config))
        
        return middlewares
    
    @staticmethod
    def development(max_concurrent: int = 5) -> list:
        """Create development-friendly middleware configuration.
        
        Args:
            max_concurrent: Maximum concurrent message processing
            
        Returns:
            List of configured middleware instances
        """
        middlewares = []
        
        middlewares.append(LoggingMiddleware(
            verbose=True,
            include_context=True,
            include_record=True
        ))
        middlewares.append(TimingMsMiddleware())
        
        store = MemoryIdempotencyStore()
        middlewares.append(IdempotencyMiddleware(
            store=store,
            ttl_seconds=300
        ))
        
        retry_config = RetryConfig(max_retries=2, base_delay=0.5)
        middlewares.append(ErrorHandlingMiddleware(retry_config=retry_config))
        
        middlewares.append(VisibilityTimeoutMonitor(
            default_visibility_timeout=30.0,
            warning_threshold=0.9
        ))
        
        parallel_config = ParallelizationConfig(
            max_concurrent_messages=max_concurrent,
            use_thread_pool=False
        )
        middlewares.append(ParallelizationMiddleware(config=parallel_config))
        
        return middlewares
    
    @staticmethod
    def minimal() -> list:
        """Create minimal middleware configuration.
        
        Returns:
            List of essential middleware instances
        """
        return [
            LoggingMiddleware(),
            TimingMsMiddleware(),
            IdempotencyMiddleware(ttl_seconds=3600)
        ]
