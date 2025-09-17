"""
Custom exceptions for JetTask WebUI Backend
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException


class JetTaskAPIException(HTTPException):
    """Base exception for JetTask API"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}


class NamespaceNotFoundError(JetTaskAPIException):
    """Namespace not found error"""
    
    def __init__(self, namespace: str):
        super().__init__(
            status_code=404,
            detail=f"Namespace '{namespace}' not found",
            error_code="NAMESPACE_NOT_FOUND",
            extra_data={"namespace": namespace}
        )


class QueueNotFoundError(JetTaskAPIException):
    """Queue not found error"""
    
    def __init__(self, queue_name: str, namespace: str = "default"):
        super().__init__(
            status_code=404,
            detail=f"Queue '{queue_name}' not found in namespace '{namespace}'",
            error_code="QUEUE_NOT_FOUND",
            extra_data={"queue_name": queue_name, "namespace": namespace}
        )


class TaskNotFoundError(JetTaskAPIException):
    """Task not found error"""
    
    def __init__(self, task_id: str):
        super().__init__(
            status_code=404,
            detail=f"Task '{task_id}' not found",
            error_code="TASK_NOT_FOUND",
            extra_data={"task_id": task_id}
        )


class ValidationError(JetTaskAPIException):
    """Validation error"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            status_code=400,
            detail=message,
            error_code="VALIDATION_ERROR",
            extra_data={"field": field} if field else {}
        )


class DatabaseConnectionError(JetTaskAPIException):
    """Database connection error"""
    
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(
            status_code=503,
            detail=message,
            error_code="DATABASE_CONNECTION_ERROR"
        )


class RateLimitError(JetTaskAPIException):
    """Rate limit exceeded error"""
    
    def __init__(self, limit: int, window: int):
        super().__init__(
            status_code=429,
            detail=f"Rate limit exceeded: {limit} requests per {window} seconds",
            error_code="RATE_LIMIT_EXCEEDED",
            extra_data={"limit": limit, "window": window}
        )


class InternalServerError(JetTaskAPIException):
    """Internal server error"""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=500,
            detail=message,
            error_code="INTERNAL_SERVER_ERROR"
        )