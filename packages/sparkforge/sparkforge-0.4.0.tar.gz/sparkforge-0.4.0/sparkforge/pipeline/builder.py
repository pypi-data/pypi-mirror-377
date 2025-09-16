"""
Refactored PipelineBuilder for SparkForge.

This module provides a clean, focused PipelineBuilder that handles only
pipeline construction, delegating execution and monitoring to specialized components.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from datetime import datetime

from pyspark.sql import SparkSession

from ..types import (
    StepName, TableName, SilverTransformFunction, GoldTransformFunction,
    ColumnRules, PipelineConfig, ExecutionConfig
)

from ..models import PipelineConfig, ParallelConfig
from .validator import PipelineValidator
from .runner import PipelineRunner
from ..models import BronzeStep, SilverStep, GoldStep
from ..logger import PipelineLogger
from ..execution import ExecutionEngine, ExecutionConfig, ExecutionMode
from ..errors.pipeline import PipelineValidationError
from ..dependencies import DependencyAnalyzer
from ..errors import (
    PipelineConfigurationError,
    StepError,
    DependencyError
)


class PipelineBuilder:
    """
    Clean, focused builder for creating data pipelines with Bronze → Silver → Gold architecture.
    
    This refactored PipelineBuilder focuses solely on pipeline construction,
    delegating execution, validation, and monitoring to specialized components.
    
    Features:
    - Fluent API for easy pipeline construction
    - Clean separation of concerns
    - Comprehensive validation
    - Better error handling
    - Extensible architecture
    
    Example:
        >>> from sparkforge import PipelineBuilder
        >>> from pyspark.sql import SparkSession, functions as F
        >>> 
        >>> spark = SparkSession.builder.appName("My Pipeline").getOrCreate()
        >>> builder = PipelineBuilder(spark=spark, schema="my_schema")
        >>> 
        >>> # Bronze layer - raw data validation
        >>> builder.with_bronze_rules(
        ...     name="events",
        ...     rules={"user_id": [F.col("user_id").isNotNull()]},
        ...     incremental_col="timestamp"
        ... )
        >>> 
        >>> # Silver layer - data transformation
        >>> builder.add_silver_transform(
        ...     name="clean_events",
        ...     source_bronze="events",
        ...     transform=lambda spark, df, silvers: df.filter(F.col("status") == "active"),
        ...     rules={"status": [F.col("status").isNotNull()]},
        ...     table_name="clean_events",
        ...     watermark_col="timestamp"
        ... )
        >>> 
        >>> # Gold layer - business analytics
        >>> builder.add_gold_transform(
        ...     name="user_analytics",
        ...     transform=lambda spark, silvers: silvers["clean_events"].groupBy("user_id").count(),
        ...     rules={"user_id": [F.col("user_id").isNotNull()]},
        ...     table_name="user_analytics",
        ...     source_silvers=["clean_events"]
        ... )
        >>> 
        >>> # Build and execute pipeline
        >>> pipeline = builder.to_pipeline()
        >>> result = pipeline.initial_load(bronze_sources={"events": source_df})
    """
    
    def __init__(
        self,
        *,
        spark: SparkSession,
        schema: str,
        min_bronze_rate: float = 95.0,
        min_silver_rate: float = 98.0,
        min_gold_rate: float = 99.0,
        verbose: bool = True,
        enable_parallel_silver: bool = True,
        max_parallel_workers: int = 4,
        execution_mode: ExecutionMode = ExecutionMode.ADAPTIVE,
        enable_caching: bool = True,
        enable_monitoring: bool = True
    ) -> None:
        """
        Initialize a new PipelineBuilder instance.
        
        Args:
            spark: Active SparkSession instance for data processing
            schema: Database schema name where tables will be created
            min_bronze_rate: Minimum data quality rate for Bronze layer (0-100)
            min_silver_rate: Minimum data quality rate for Silver layer (0-100)
            min_gold_rate: Minimum data quality rate for Gold layer (0-100)
            verbose: Enable verbose logging output
            enable_parallel_silver: Allow parallel execution of independent Silver steps
            max_parallel_workers: Maximum number of parallel workers for Silver steps
            execution_mode: Execution strategy (ADAPTIVE, SEQUENTIAL, PARALLEL)
            enable_caching: Enable DataFrame caching for performance optimization
            enable_monitoring: Enable comprehensive execution monitoring
            
        Raises:
            ValueError: If quality rates are not between 0 and 100
            RuntimeError: If Spark session is not active
        """
        # Validate inputs
        if not spark:
            raise PipelineConfigurationError(
                "Spark session is required",
                suggestions=["Ensure SparkSession is properly initialized", "Check Spark configuration"]
            )
        if not schema:
            raise PipelineConfigurationError(
                "Schema name cannot be empty",
                suggestions=["Provide a valid schema name", "Check database configuration"]
            )
        
        # Store configuration
        from ..models import ValidationThresholds
        thresholds = ValidationThresholds(
            bronze=min_bronze_rate,
            silver=min_silver_rate,
            gold=min_gold_rate
        )
        parallel_config = ParallelConfig(
            enabled=enable_parallel_silver,
            max_workers=max_parallel_workers
        )
        self.config = PipelineConfig(
            schema=schema,
            thresholds=thresholds,
            parallel=parallel_config,
            verbose=verbose
        )
        
        # Initialize components
        self.spark = spark
        self.logger = PipelineLogger(verbose=verbose)
        self.validator = PipelineValidator(self.logger)
        
        # Expose schema for backward compatibility
        self.schema = schema
        self.pipeline_id = f"pipeline_{schema}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Expose validators for backward compatibility
        self.validators = self.validator.custom_validators
        
        # Pipeline definition
        self.bronze_steps: Dict[str, BronzeStep] = {}
        self.silver_steps: Dict[str, SilverStep] = {}
        self.gold_steps: Dict[str, GoldStep] = {}
        
        self.logger.info(f"🔧 PipelineBuilder initialized (schema: {schema})")
    
    def with_bronze_rules(
        self,
        *,
        name: StepName,
        rules: ColumnRules,
        incremental_col: Optional[str] = None,
        description: Optional[str] = None
    ) -> 'PipelineBuilder':
        """
        Add Bronze layer validation rules for raw data.
        
        Bronze steps represent the first layer of the Medallion Architecture,
        handling raw data ingestion and basic validation.
        
        Args:
            name: Unique identifier for this Bronze step
            rules: Dictionary mapping column names to validation rule lists.
                   Each rule should be a PySpark Column expression.
            incremental_col: Column name for incremental processing (e.g., "timestamp", "updated_at").
                            If provided, enables incremental processing with append mode.
            description: Optional description of this Bronze step
            
        Returns:
            Self for method chaining
            
        Example:
            >>> builder.with_bronze_rules(
            ...     name="user_events",
            ...     rules={"user_id": [F.col("user_id").isNotNull()]},
            ...     incremental_col="timestamp"
            ... )
        """
        if not name:
            raise StepError(
                "Bronze step name cannot be empty",
                step_name=name or "unknown",
                step_type="bronze",
                suggestions=["Provide a valid step name", "Check step naming conventions"]
            )
        
        if name in self.bronze_steps:
            raise StepError(
                f"Bronze step '{name}' already exists",
                step_name=name,
                step_type="bronze",
                suggestions=["Use a different step name", "Remove the existing step first"]
            )
        
        # Create bronze step
        bronze_step = BronzeStep(
            name=name,
            rules=rules,
            incremental_col=incremental_col
        )
        
        self.bronze_steps[name] = bronze_step
        self.logger.info(f"✅ Added Bronze step: {name}")
        
        return self
    
    def with_silver_rules(
        self,
        *,
        name: StepName,
        table_name: TableName,
        rules: ColumnRules,
        watermark_col: Optional[str] = None,
        description: Optional[str] = None
    ) -> 'PipelineBuilder':
        """
        Add existing Silver layer table for validation and monitoring.
        
        This method is used when you have an existing Silver table that you want to
        include in the pipeline for validation and monitoring purposes, but don't
        need to transform the data.
        
        Args:
            name: Unique identifier for this Silver step
            table_name: Existing Delta table name
            rules: Dictionary mapping column names to validation rule lists
            watermark_col: Column name for watermarking (optional)
            description: Optional description of this Silver step
            
        Returns:
            Self for method chaining
            
        Example:
            >>> builder.with_silver_rules(
            ...     name="existing_clean_events",
            ...     table_name="clean_events",
            ...     rules={"user_id": [F.col("user_id").isNotNull()]},
            ...     watermark_col="updated_at"
            ... )
        """
        if not name:
            raise StepError(
                "Silver step name cannot be empty",
                step_name=name or "unknown",
                step_type="silver",
                suggestions=["Provide a valid step name", "Check step naming conventions"]
            )
        
        if name in self.silver_steps:
            raise StepError(
                f"Silver step '{name}' already exists",
                step_name=name,
                step_type="silver",
                suggestions=["Use a different step name", "Remove the existing step first"]
            )
        
        # Create SilverStep for existing table
        silver_step = SilverStep(
            name=name,
            source_bronze="",  # No source for existing tables
            transform=None,    # No transform for existing tables
            rules=rules,
            table_name=table_name,
            watermark_col=watermark_col,
            existing=True
        )
        
        self.silver_steps[name] = silver_step
        self.logger.info(f"✅ Added existing Silver step: {name}")
        
        return self
    
    def add_validator(self, validator: 'StepValidator') -> 'PipelineBuilder':
        """
        Add a custom step validator to the pipeline.
        
        Custom validators allow you to add additional validation logic
        beyond the built-in validation rules.
        
        Args:
            validator: Custom validator implementing StepValidator protocol
            
        Returns:
            Self for method chaining
            
        Example:
            >>> class CustomValidator(StepValidator):
            ...     def validate(self, step, context):
            ...         if step.name == "special_step":
            ...             return ["Special validation failed"]
            ...         return []
            >>> 
            >>> builder.add_validator(CustomValidator())
        """
        self.validator.add_validator(validator)
        return self
    
    def add_silver_transform(
        self,
        *,
        name: StepName,
        source_bronze: StepName,
        transform: SilverTransformFunction,
        rules: ColumnRules,
        table_name: TableName,
        watermark_col: Optional[str] = None,
        description: Optional[str] = None,
        depends_on: Optional[List[StepName]] = None
    ) -> 'PipelineBuilder':
        """
        Add Silver layer transformation step for data cleaning and enrichment.
        
        Silver steps represent the second layer of the Medallion Architecture,
        transforming raw Bronze data into clean, business-ready datasets.
        
        Args:
            name: Unique identifier for this Silver step
            source_bronze: Name of the Bronze step this Silver step depends on
            transform: Transformation function with signature:
                     (spark: SparkSession, bronze_df: DataFrame, prior_silvers: Dict[str, DataFrame]) -> DataFrame
            rules: Dictionary mapping column names to validation rule lists.
                   Each rule should be a PySpark Column expression.
            table_name: Target Delta table name where results will be stored
            watermark_col: Column name for watermarking (e.g., "timestamp", "updated_at").
                          If provided, enables incremental processing with append mode.
            description: Optional description of this Silver step
            depends_on: List of other Silver step names that must complete before this step.
            
        Returns:
            Self for method chaining
            
        Example:
            >>> def clean_user_events(spark, bronze_df, prior_silvers):
            ...     return (bronze_df
            ...         .filter(F.col("user_id").isNotNull())
            ...         .withColumn("event_date", F.date_trunc("day", "timestamp"))
            ...     )
            >>> 
            >>> builder.add_silver_transform(
            ...     name="clean_events",
            ...     source_bronze="user_events",
            ...     transform=clean_user_events,
            ...     rules={"user_id": [F.col("user_id").isNotNull()]},
            ...     table_name="clean_user_events",
            ...     watermark_col="timestamp"
            ... )
        """
        if not name:
            raise StepError(
                "Silver step name cannot be empty",
                step_name=name or "unknown",
                step_type="silver",
                suggestions=["Provide a valid step name", "Check step naming conventions"]
            )
        
        if name in self.silver_steps:
            raise StepError(
                f"Silver step '{name}' already exists",
                step_name=name,
                step_type="silver",
                suggestions=["Use a different step name", "Remove the existing step first"]
            )
        
        # Note: Dependency validation is deferred to validate_pipeline()
        # This allows for more flexible pipeline construction
        
        # Create silver step
        silver_step = SilverStep(
            name=name,
            source_bronze=source_bronze,
            transform=transform,
            rules=rules,
            table_name=table_name,
            watermark_col=watermark_col
        )
        
        self.silver_steps[name] = silver_step
        self.logger.info(f"✅ Added Silver step: {name} (source: {source_bronze})")
        
        return self
    
    def add_gold_transform(
        self,
        *,
        name: StepName,
        transform: GoldTransformFunction,
        rules: ColumnRules,
        table_name: TableName,
        source_silvers: List[StepName],
        description: Optional[str] = None
    ) -> 'PipelineBuilder':
        """
        Add Gold layer transformation step for business analytics and aggregations.
        
        Gold steps represent the third layer of the Medallion Architecture,
        creating business-ready datasets for analytics and reporting.
        
        Args:
            name: Unique identifier for this Gold step
            transform: Transformation function with signature:
                     (spark: SparkSession, silvers: Dict[str, DataFrame]) -> DataFrame
            rules: Dictionary mapping column names to validation rule lists.
                   Each rule should be a PySpark Column expression.
            table_name: Target Delta table name where results will be stored
            source_silvers: List of Silver step names this Gold step depends on
            description: Optional description of this Gold step
            
        Returns:
            Self for method chaining
            
        Example:
            >>> def user_daily_metrics(spark, silvers):
            ...     events_df = silvers["clean_events"]
            ...     return (events_df
            ...         .groupBy("user_id", "event_date")
            ...         .agg(F.count("*").alias("event_count"))
            ...     )
            >>> 
            >>> builder.add_gold_transform(
            ...     name="user_metrics",
            ...     transform=user_daily_metrics,
            ...     rules={"user_id": [F.col("user_id").isNotNull()]},
            ...     table_name="user_daily_metrics",
            ...     source_silvers=["clean_events"]
            ... )
        """
        if not name:
            raise StepError(
                "Gold step name cannot be empty",
                step_name=name or "unknown",
                step_type="gold",
                suggestions=["Provide a valid step name", "Check step naming conventions"]
            )
        
        if name in self.gold_steps:
            raise StepError(
                f"Gold step '{name}' already exists",
                step_name=name,
                step_type="gold",
                suggestions=["Use a different step name", "Remove the existing step first"]
            )
        
        # Handle source_silvers=None (use all available silvers)
        if source_silvers is None:
            source_silvers = list(self.silver_steps.keys())
        
        # Note: Dependency validation is deferred to validate_pipeline()
        # This allows for more flexible pipeline construction
        
        # Create gold step
        gold_step = GoldStep(
            name=name,
            transform=transform,
            rules=rules,
            table_name=table_name,
            source_silvers=source_silvers
        )
        
        self.gold_steps[name] = gold_step
        self.logger.info(f"✅ Added Gold step: {name} (sources: {source_silvers})")
        
        return self
    
    def validate_pipeline(self) -> List[str]:
        """
        Validate the entire pipeline configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        validation_result = self.validator.validate_pipeline(
            self.config,
            self.bronze_steps,
            self.silver_steps,
            self.gold_steps
        )
        
        if validation_result.errors:
            self.logger.error(f"Pipeline validation failed with {len(validation_result.errors)} errors")
            for error in validation_result.errors:
                self.logger.error(f"  - {error}")
        else:
            self.logger.info("✅ Pipeline validation passed")
        
        return validation_result.errors
    
    def to_pipeline(self) -> PipelineRunner:
        """
        Build and return a PipelineRunner for executing this pipeline.
        
        Returns:
            PipelineRunner instance ready for execution
            
        Raises:
            ValueError: If pipeline validation fails
        """
        # Validate pipeline before building
        validation_errors = self.validate_pipeline()
        if validation_errors:
            raise ValueError(
                f"Pipeline validation failed with {len(validation_errors)} errors: {', '.join(validation_errors)}"
            )
        
        # Create execution engine
        execution_config = ExecutionConfig(
            mode=ExecutionMode.ADAPTIVE,
            max_workers=self.config.parallel.max_workers,
            timeout_seconds=300
        )
        
        execution_engine = ExecutionEngine(
            spark=self.spark,
            logger=self.logger,
            config=execution_config,
            thresholds={
                "bronze": self.config.thresholds.bronze,
                "silver": self.config.thresholds.silver,
                "gold": self.config.thresholds.gold
            },
            schema=self.config.schema
        )
        
        # Create dependency analyzer
        dependency_analyzer = DependencyAnalyzer(logger=self.logger)
        
        # Create pipeline runner
        runner = PipelineRunner(
            spark=self.spark,
            config=self.config,
            bronze_steps=self.bronze_steps,
            silver_steps=self.silver_steps,
            gold_steps=self.gold_steps,
            logger=self.logger,
            execution_engine=execution_engine,
            dependency_analyzer=dependency_analyzer
        )
        
        self.logger.info(f"🚀 Pipeline built successfully with {len(self.bronze_steps)} bronze, {len(self.silver_steps)} silver, {len(self.gold_steps)} gold steps")
        
        return runner
