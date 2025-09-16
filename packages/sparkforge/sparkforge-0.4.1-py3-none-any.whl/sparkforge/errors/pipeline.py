"""
Pipeline-specific exceptions for SparkForge.

This module defines exceptions specific to pipeline operations,
providing detailed error context for pipeline-related issues.
"""

from __future__ import annotations
from typing import Optional, List

from .base import SparkForgeError, ErrorCategory, ErrorSeverity


class PipelineError(SparkForgeError):
    """Base exception for all pipeline-related errors."""
    
    def __init__(
        self,
        message: str,
        *,
        pipeline_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.pipeline_id = pipeline_id
        self.execution_id = execution_id
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.pipeline_id:
            return f"[Pipeline: {self.pipeline_id}] {base_msg}"
        return base_msg


class PipelineConfigurationError(PipelineError):
    """Raised when pipeline configuration is invalid."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class PipelineExecutionError(PipelineError):
    """Raised when pipeline execution fails."""
    
    def __init__(
        self,
        message: str,
        *,
        step_name: Optional[str] = None,
        step_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.EXECUTION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.step_name = step_name
        self.step_type = step_type
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.step_name:
            return f"[Step: {self.step_name}] {base_msg}"
        return base_msg


class PipelineValidationError(PipelineError):
    """Raised when pipeline validation fails."""
    
    def __init__(
        self,
        message: str,
        *,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        self.validation_errors = validation_errors or []
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.validation_errors:
            errors_str = "; ".join(self.validation_errors)
            return f"{base_msg} | Validation errors: {errors_str}"
        return base_msg


class StepError(SparkForgeError):
    """Base exception for step-related errors."""
    
    def __init__(
        self,
        message: str,
        *,
        step_name: str,
        step_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.step_name = step_name
        self.step_type = step_type
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        return f"[{self.step_name}] {base_msg}"


class StepExecutionError(StepError):
    """Raised when a step fails during execution."""
    
    def __init__(
        self,
        message: str,
        *,
        step_name: str,
        step_type: Optional[str] = None,
        retry_count: int = 0,
        **kwargs
    ):
        super().__init__(
            message,
            step_name=step_name,
            step_type=step_type,
            category=ErrorCategory.EXECUTION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.retry_count = retry_count
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.retry_count > 0:
            return f"{base_msg} (Retry #{self.retry_count})"
        return base_msg


class StepValidationError(StepError):
    """Raised when step validation fails."""
    
    def __init__(
        self,
        message: str,
        *,
        step_name: str,
        step_type: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            step_name=step_name,
            step_type=step_type,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        self.validation_errors = validation_errors or []
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.validation_errors:
            errors_str = "; ".join(self.validation_errors)
            return f"{base_msg} | Validation errors: {errors_str}"
        return base_msg


class DependencyError(SparkForgeError):
    """Raised when dependency-related errors occur."""
    
    def __init__(
        self,
        message: str,
        *,
        step_name: Optional[str] = None,
        dependency_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.EXECUTION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.step_name = step_name
        self.dependency_name = dependency_name
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.step_name and self.dependency_name:
            return f"[{self.step_name} -> {self.dependency_name}] {base_msg}"
        elif self.step_name:
            return f"[{self.step_name}] {base_msg}"
        return base_msg


class CircularDependencyError(DependencyError):
    """Raised when circular dependencies are detected."""
    
    def __init__(
        self,
        message: str,
        *,
        cycle: List[str],
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.cycle = cycle
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        cycle_str = " -> ".join(self.cycle)
        return f"{base_msg} | Cycle: {cycle_str}"


class InvalidDependencyError(DependencyError):
    """Raised when invalid dependencies are detected."""
    
    def __init__(
        self,
        message: str,
        *,
        invalid_dependencies: List[str],
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.invalid_dependencies = invalid_dependencies
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        deps_str = ", ".join(self.invalid_dependencies)
        return f"{base_msg} | Invalid dependencies: {deps_str}"
