# # # # Copyright (c) 2024 Odos Matthews
# # # #
# # # # Permission is hereby granted, free of charge, to any person obtaining a copy
# # # # of this software and associated documentation files (the "Software"), to deal
# # # # in the Software without restriction, including without limitation the rights
# # # # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # # # copies of the Software, and to permit persons to whom the Software is
# # # # furnished to do so, subject to the following conditions:
# # # #
# # # # The above copyright notice and this permission notice shall be included in all
# # # # copies or substantial portions of the Software.
# # # #
# # # # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # # # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # # # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # # # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # # # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # # # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # # # SOFTWARE.
# #
# # # Copyright (c) 2024 Odos Matthews
# # #
# # # Permission is hereby granted, free of charge, to any person obtaining a copy
# # # of this software and associated documentation files (the "Software"), to deal
# # # in the Software without restriction, including without limitation the rights
# # # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # # copies of the Software, and to permit persons to whom the Software is
# # # furnished to do so, subject to the following conditions:
# # #
# # # The above copyright notice and this permission notice shall be included in all
# # # copies or substantial portions of the Software.
# # #
# # # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # # SOFTWARE.
#
# # # Copyright (c) 2024 Odos Matthews
# # #
# # # Permission is hereby granted, free of charge, to any person obtaining a copy
# # # of this software and associated documentation files (the "Software"), to deal
# # # in the Software without restriction, including without limitation the rights
# # # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # # copies of the Software, and to permit persons to whom the Software is
# # # furnished to do so, subject to the following conditions:
# # #
# # # The above copyright notice and this permission notice shall be included in all
# # # copies or substantial portions of the Software.
# # #
# # # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # # SOFTWARE.
#
# # Copyright (c) 2024 Odos Matthews
# #
# # Permission is hereby granted, free of charge, to any person obtaining a copy
# # of this software and associated documentation files (the "Software"), to deal
# # in the Software without restriction, including without limitation the rights
# # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # copies of the Software, and to permit persons to whom the Software is
# # furnished to do so, subject to the following conditions:
# #
# # The above copyright notice and this permission notice shall be included in all
# # copies or substantial portions of the Software.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# # SOFTWARE.

#


# validation.py
"""
Data validation utilities for the SparkForge pipeline framework.

This module provides comprehensive data validation capabilities for the Medallion Architecture,
including column-level validation, data quality assessment, and quality threshold enforcement.

Key Features:
- Column-level validation with PySpark expressions
- Data quality rate calculation and threshold enforcement
- Flexible rule definition system supporting custom validations
- Comprehensive validation reporting with detailed statistics
- Integration with Bronze, Silver, and Gold layer validation
- Performance-optimized validation with caching support

The validation system ensures data quality at each layer of the pipeline,
preventing low-quality data from propagating through the system.
"""

from __future__ import annotations

import logging
import time

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType

from .errors.data import ValidationError
from .models import ColumnRules, StageStats
from .performance_cache import cached_validation
from .security import get_security_manager

logger = logging.getLogger(__name__)


def _convert_rule_to_expression(rule: str, column_name: str) -> object | str:
    """
    Convert a string rule to a PySpark Column expression.

    Args:
        rule: String rule name (e.g., "not_null", "positive")
        column_name: Name of the column to apply the rule to

    Returns:
        PySpark Column expression
    """
    if rule == "not_null":
        return F.col(column_name).isNotNull()
    elif rule == "positive":
        return F.col(column_name) > 0
    elif rule == "non_negative":
        return F.col(column_name) >= 0
    elif rule == "non_zero":
        return F.col(column_name) != 0
    else:
        # For unknown rules, assume it's a valid PySpark expression
        # This allows for custom rules to be passed as expressions
        return rule


def _convert_rules_to_expressions(
    rules: ColumnRules,
) -> dict[str, list[DataFrame | str | bool]]:
    """
    Convert string rules to PySpark Column expressions.

    Args:
        rules: Dictionary of column rules (can contain strings or expressions)

    Returns:
        Dictionary with all rules converted to PySpark expressions
    """
    converted_rules = {}
    for column_name, rule_list in rules.items():
        converted_rule_list = []
        for rule in rule_list:
            if isinstance(rule, str):
                converted_rule_list.append(
                    _convert_rule_to_expression(rule, column_name)
                )
            else:
                # Already a PySpark expression
                converted_rule_list.append(rule)
        converted_rules[column_name] = converted_rule_list
    return converted_rules


def and_all_rules(rules: ColumnRules) -> object | bool:
    """
    Combine all validation rules with AND logic.

    Args:
        rules: Dictionary of column rules (can contain strings or expressions)

    Returns:
        Combined predicate expression
    """
    if not rules:
        # Return a simple boolean instead of F.lit(True) to avoid Spark context requirement
        return True

    # Convert string rules to PySpark expressions
    converted_rules = _convert_rules_to_expressions(rules)

    # Start with the first expression, then combine with others
    expressions = []
    for _, exprs in converted_rules.items():
        expressions.extend(exprs)

    if not expressions:
        return True

    # Ensure all expressions are PySpark Column objects
    pred = expressions[0]
    for e in expressions[1:]:
        # Check if both are PySpark Column objects by checking for specific methods
        if (
            hasattr(pred, "__and__")
            and hasattr(e, "__and__")
            and hasattr(pred, "__rand__")
            and hasattr(e, "__rand__")
            and hasattr(pred, "isNull")
            and hasattr(e, "isNull")
        ):
            pred = pred & e  # type: ignore
        else:
            # If either is not a Column, convert to boolean logic
            pred = bool(pred) and bool(e)

    return pred


def validate_dataframe_schema(df: DataFrame, expected_columns: list[str]) -> bool:
    """
    Validate that DataFrame has expected columns.

    Args:
        df: DataFrame to validate
        expected_columns: List of expected column names

    Returns:
        True if schema is valid, False otherwise
    """
    actual_columns = set(df.columns)
    expected_columns_set = set(expected_columns)

    missing_columns = expected_columns_set - actual_columns
    if missing_columns:
        logger.warning(f"Missing columns: {missing_columns}")
        return False

    return True


def get_dataframe_info(
    df: DataFrame,
) -> dict[str, str | int | float | bool | list[str] | dict[str, str]]:
    """
    Get comprehensive information about a DataFrame.

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary with DataFrame information
    """
    try:
        row_count = df.count()
        column_count = len(df.columns)
        schema = df.schema

        return {
            "row_count": row_count,
            "column_count": column_count,
            "columns": df.columns,
            "schema": str(schema),
            "is_empty": row_count == 0,
        }
    except Exception as e:
        logger.error(f"Failed to get DataFrame info: {e}")
        return {
            "row_count": 0,
            "column_count": 0,
            "columns": [],
            "schema": "unknown",
            "is_empty": True,
            "error": str(e),
        }


@cached_validation
def apply_column_rules(
    df: DataFrame,
    rules: ColumnRules,
    stage: str,
    step: str,
    filter_columns_by_rules: bool = True,
) -> tuple[DataFrame, DataFrame, StageStats]:
    """
    Apply validation rules to a DataFrame and return valid/invalid DataFrames with statistics.

    This function is the core validation engine for SparkForge pipelines. It applies
    column-level validation rules to a DataFrame and separates valid from invalid records,
    providing comprehensive statistics about data quality.

    Args:
        df: DataFrame to validate. Must contain the columns referenced in the rules.
        rules: Dictionary mapping column names to lists of validation rules.
               Rules can be PySpark Column expressions or string shortcuts:
               - "not_null": Column must not be null
               - "positive": Column must be greater than 0
               - "non_negative": Column must be >= 0
               - "non_zero": Column must not equal 0
               - Custom PySpark expressions for complex validations
        stage: Pipeline stage name ("bronze", "silver", or "gold").
              Used for logging and statistics tracking.
        step: Step name within the stage. Used for logging and statistics tracking.
        filter_columns_by_rules: If True (default), the output DataFrames will only contain
                                columns that have validation rules defined. If False, all
                                columns from the input DataFrame will be preserved.

    Returns:
        Tuple containing:
        - valid_df: DataFrame containing only records that passed all validation rules
        - invalid_df: DataFrame containing records that failed validation rules.
                    Includes additional "__validation_failures__" column with failure details.
        - stats: StageStats object with comprehensive validation statistics including:
                total_rows, valid_rows, invalid_rows, validation_rate, duration_secs

    Raises:
        ValidationError: If validation rules are None or validation process fails

    Example:
        >>> from pyspark.sql import functions as F
        >>>
        >>> # Define validation rules
        >>> rules = {
        ...     "user_id": [F.col("user_id").isNotNull(), F.col("user_id") > 0],
        ...     "email": ["not_null", F.col("email").contains("@")],
        ...     "age": ["non_negative", F.col("age") < 120],
        ...     "status": [F.col("status").isin(["active", "inactive", "pending"])]
        ... }
        >>>
        >>> # Apply validation (filters columns to only those with rules)
        >>> valid_df, invalid_df, stats = apply_column_rules(
        ...     df=raw_data_df,
        ...     rules=rules,
        ...     stage="bronze",
        ...     step="user_events",
        ...     filter_columns_by_rules=True
        ... )
        >>>
        >>> # Apply validation (preserves all columns)
        >>> valid_df, invalid_df, stats = apply_column_rules(
        ...     df=raw_data_df,
        ...     rules=rules,
        ...     stage="bronze",
        ...     step="user_events",
        ...     filter_columns_by_rules=False
        ... )
        >>>
        >>> # Check results
        >>> print(f"Validation rate: {stats.validation_rate:.2f}%")
        >>> print(f"Valid rows: {stats.valid_rows}")
        >>> print(f"Invalid rows: {stats.invalid_rows}")
        >>>
        >>> # Process valid data
        >>> clean_df = valid_df.filter(F.col("status") == "active")
        >>>
        >>> # Analyze invalid data
        >>> if stats.invalid_rows > 0:
        ...     invalid_df.select("__validation_failures__").show(truncate=False)
    """
    if rules is None:
        raise ValidationError(f"[{stage}:{step}] Validation rules cannot be None.")

    # Validate inputs for security
    security_manager = get_security_manager()
    try:
        validated_rules = security_manager.validate_validation_rules(rules)
    except Exception as e:
        logger.warning(f"[{stage}:{step}] Security validation failed: {e}")
        validated_rules = rules  # Fallback to original rules

    t0 = time.time()

    # Cache the DataFrame for multiple operations to avoid recomputation
    df.cache()

    # Optimize: Get total count only once and cache it
    total = df.count()
    logger.debug(f"[{stage}:{step}] Total rows to validate: {total}")

    if validated_rules:
        # Convert string rules to PySpark expressions
        converted_rules = _convert_rules_to_expressions(validated_rules)
        logger.debug(f"[{stage}:{step}] Original rules: {validated_rules}")
        logger.debug(f"[{stage}:{step}] Converted rules: {converted_rules}")
        pred = and_all_rules(converted_rules)
        marked = df.withColumn("__is_valid__", pred)

        # Cache the marked DataFrame to avoid recomputation
        marked.cache()

        valid_df = marked.filter(F.col("__is_valid__")).drop("__is_valid__")
        invalid_df = marked.filter(~F.col("__is_valid__")).drop("__is_valid__")

        # Optimize: Calculate counts more efficiently using a single action
        # Use collect() to get both counts in one operation
        valid_count = valid_df.count()
        invalid_count = total - valid_count
        logger.debug(
            f"[{stage}:{step}] Validation completed - valid rows: {valid_count}, invalid rows: {invalid_count}"
        )

        # Add detailed failure information
        failed_arrays = []
        for col_name, exprs in converted_rules.items():
            for idx, expr in enumerate(exprs):
                tag = F.lit(f"{col_name}#{idx + 1}")
                # Ensure expr is a Column before applying ~ operator
                if hasattr(expr, "__invert__"):
                    failed_arrays.append(
                        F.when(~expr, F.array(tag)).otherwise(  # type: ignore
                            F.array().cast(ArrayType(StringType()))
                        )
                    )
                else:
                    # If not a Column, skip this rule
                    continue

        if failed_arrays:
            invalid_df = invalid_df.withColumn(
                "_failed_rules", F.array_distinct(F.flatten(F.array(*failed_arrays)))
            )
    else:
        valid_df, invalid_df = df, df.limit(0)
        valid_count = total
        invalid_count = 0

    rate = safe_divide(valid_count * 100.0, total, 100.0)

    # Column selection based on filter_columns_by_rules parameter
    if filter_columns_by_rules:
        # Select only columns that have rules (if any) for all stages
        keep_cols = (
            [c for c in rules.keys() if c in valid_df.columns]
            if rules
            else valid_df.columns
        )
        valid_proj = valid_df.select(*keep_cols) if keep_cols else valid_df

        # For invalid DataFrame, keep rule columns plus _failed_rules if it exists
        invalid_keep_cols = keep_cols.copy() if keep_cols else []
        if "_failed_rules" in invalid_df.columns:
            invalid_keep_cols.append("_failed_rules")

        # Only apply column filtering if we have columns to keep
        if invalid_keep_cols:
            invalid_proj = invalid_df.select(*invalid_keep_cols)
        else:
            invalid_proj = invalid_df

        logger.debug(
            f"[{stage}:{step}] Filtering columns based on rules keys: {list(rules.keys()) if rules else 'no rules'}"
        )
        logger.debug(f"[{stage}:{step}] Available columns: {valid_df.columns}")
        logger.debug(f"[{stage}:{step}] Keeping columns: {keep_cols}")
        logger.debug(f"[{stage}:{step}] Invalid keeping columns: {invalid_keep_cols}")
    else:
        # Preserve all columns from the original DataFrame
        valid_proj = valid_df
        invalid_proj = invalid_df
        logger.debug(f"[{stage}:{step}] Preserving all columns: {valid_df.columns}")
    logger.debug(f"[{stage}:{step}] Final columns: {valid_proj.columns}")

    stats = StageStats(
        stage=stage,
        step=step,
        total_rows=total,
        valid_rows=valid_count,
        invalid_rows=invalid_count,
        validation_rate=rate,
        duration_secs=round(time.time() - t0, 6),
    )

    logger.info(
        f"Validation completed for {stage}:{step} - {valid_count}/{total} rows valid ({rate:.2f}%)"
    )
    return valid_proj, invalid_proj, stats


def assess_data_quality(
    df: DataFrame, rules: ColumnRules | None = None
) -> dict[str, str | int | float | bool | list[str] | dict[str, str]]:
    """
    Assess data quality of a DataFrame.

    Args:
        df: DataFrame to assess
        rules: Optional validation rules

    Returns:
        Dictionary with data quality metrics
    """
    info = get_dataframe_info(df)

    if info["is_empty"]:
        return {
            "total_rows": 0,
            "quality_score": 100.0,
            "issues": ["Empty dataset"],
            "recommendations": ["Check data source"],
        }

    total_rows = info["row_count"]
    quality_issues = []
    recommendations = []

    # Cache DataFrame for multiple operations
    df.cache()

    # Check for null values - optimize by calculating all null counts in one operation
    null_counts = {}
    null_checks = []
    for col in df.columns:
        null_checks.append(
            F.sum(F.when(F.col(col).isNull(), 1).otherwise(0)).alias(f"{col}_nulls")
        )

    if null_checks:
        # Single action to get all null counts
        null_results = df.select(*null_checks).collect()[0]
        for col in df.columns:
            null_count = getattr(null_results, f"{col}_nulls", 0)
            if null_count > 0:
                null_counts[col] = null_count
                null_percentage = (null_count / total_rows) * 100
                if null_percentage > 50:
                    quality_issues.append(
                        f"High null percentage in {col}: {null_percentage:.1f}%"
                    )
                    recommendations.append(f"Investigate null values in {col}")

    # Check for duplicates - optimize by using distinct count
    distinct_count = df.distinct().count()
    duplicate_count = total_rows - distinct_count
    if duplicate_count > 0:
        duplicate_percentage = (duplicate_count / total_rows) * 100
        quality_issues.append(
            f"Duplicate rows: {duplicate_count} ({duplicate_percentage:.1f}%)"
        )
        recommendations.append("Consider deduplication strategy")

    # Apply validation rules if provided
    if rules:
        try:
            _, _, stats = apply_column_rules(
                df, rules, "quality_check", "assessment", filter_columns_by_rules=False
            )
            if stats.validation_rate < 95:
                quality_issues.append(
                    f"Low validation rate: {stats.validation_rate:.1f}%"
                )
                recommendations.append("Review data validation rules")
        except Exception as e:
            quality_issues.append(f"Validation error: {e}")

    # Calculate quality score
    quality_score = 100.0
    if quality_issues:
        quality_score = max(0, 100 - len(quality_issues) * 10)

    return {
        "total_rows": total_rows,
        "quality_score": quality_score,
        "null_counts": null_counts,
        "duplicate_rows": duplicate_count,
        "issues": quality_issues,
        "recommendations": recommendations,
    }


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if denominator is zero

    Returns:
        Division result or default value
    """
    return numerator / denominator if denominator != 0 else default
