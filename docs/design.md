# Lightdash Pre-commit Hooks - Technical Specification

## Overview

This specification defines a lightweight set of pre-commit hooks for validating Lightdash-specific configurations in dbt schema files. The hooks operate by parsing YAML files directly and validating the `meta` sections that contain Lightdash configurations, without requiring dbt-core or a full dbt environment.

## DBT Version Support

### Supported Versions

The tool supports multiple dbt Core versions to handle schema evolution:

1. **dbt 1.9 and below**: `meta` and `tags` properties at model/column level
2. **dbt 1.10 and above**: `meta` and `tags` nested under `config` blocks

### Version Detection

The parser automatically detects dbt version based on schema structure and normalizes to a consistent internal format for validation.

### Migration Support

The tool includes built-in support for projects transitioning between versions:

- **Auto-detection**: Automatically identifies schema version per file
- **Mixed projects**: Supports projects with both old and new formats
- **Normalization**: Internally converts v1.9 format to v1.10 for consistent validation
- **Migration warnings**: Optionally warns about deprecated v1.9 format usage

## Hook Specifications

### Core Validation Hooks

#### `validate-lightdash-schema`

**Purpose**: Validate Lightdash configurations against the official JSON schema

**Files**: `**/schema.yml`, `**/schema.yaml`, `**/_schema.yml`

**Requirements**:

- Must validate against `lightdash-dbt-2.0.json` schema
- Support for custom schema file paths via `--schema-path` argument
- Validate nested structures: `meta.metrics`, `meta.dimension`, `meta.joins`

**Arguments**:

- `--schema-path`: Path to Lightdash schema file (default: uses bundled schema)
- `--model-filter`: Regex pattern to filter specific models

**Exit codes**:

- `0`: All validations pass
- `1`: Schema validation failures found

#### `check-metric-definitions`

**Purpose**: Validate metric configurations in model schema files

**Validation Rules**:

1. **Required Fields**:

   - `type`: Must be one of `[percentile, median, average, boolean, count, count_distinct, date, max, min, number, string, sum]`
   - `sql`: Must be non-empty string (unless type is `count`)

2. **Optional Field Validation**:

   - `label`: If present, must be non-empty string with minimum length 1
   - `description`: If present, must be non-empty string with minimum length 1
   - `hidden`: Must be boolean if present
   - `round`: Must be number ≥ 0 if present
   - `percentile`: Must be number if type is `percentile`

3. **Business Logic**:
   - `percentile` field required when type is `percentile`
   - `sql` field optional when type is `count`

**Arguments**:

- `--require-description`: Fail if metrics lack descriptions
- `--require-labels`: Fail if metrics lack labels
- `--min-description-length N`: Minimum description length (default: 10)

#### `check-dimension-definitions`

**Purpose**: Validate dimension configurations

**Validation Rules**:

1. **Type Validation**:

   - `type`: Must be one of `[string, number, timestamp, date, boolean]`

2. **Time Dimension Validation**:

   - `time_intervals`: Must be array of valid intervals or string `"default"/"OFF"`
   - Valid intervals: `[RAW, DAY, WEEK, MONTH, QUARTER, YEAR, HOUR, MINUTE, SECOND, MILLISECOND, WEEK_NUM, MONTH_NUM, MONTH_NAME, DAY_OF_WEEK_NAME, QUARTER_NAME, DAY_OF_WEEK_INDEX, DAY_OF_MONTH_NUM, DAY_OF_YEAR_NUM, QUARTER_NUM, YEAR_NUM, HOUR_OF_DAY_NUM, MINUTE_OF_HOUR_NUM]`

3. **SQL Field Validation**:
   - `sql`: If present, must be non-empty string
   - Check for basic field reference syntax (no warehouse-specific validation)

**Arguments**:

- `--require-time-intervals`: Require time_intervals for timestamp/date dimensions
- `--require-sql-for-additional`: Require SQL for additional_dimensions

#### `validate-joins`

**Purpose**: Validate join definitions in model meta

**Validation Rules**:

1. **Required Fields**:

   - `join`: Must be non-empty string
   - `sql_on`: Must be non-empty string

2. **Reference Syntax**:

   - Join condition must use Lightdash `${model.field}` reference syntax
   - Check for proper field reference formatting

3. **Basic Structure Check**:
   - Validate join condition contains required elements
   - Ensure join references use consistent syntax

**Arguments**:

- `--check-references`: Enable field reference validation (default: true)

### Organization & Quality Hooks

#### `check-group-labels`

**Purpose**: Validate group label consistency and hierarchy

**Validation Rules**:

1. **Group Label Requirements**:

   - All metrics and dimensions must have `groups` array (unless `hidden: true`)
   - Groups array must contain 1-3 elements (max 3 levels)
   - Group names must match allowed taxonomy if configured

2. **Consistency Checks**:
   - Same group names should have consistent casing across models
   - Detect similar group names that might be typos

**Configuration Schema**:

- `enforce`: Boolean flag to enable group label validation
- `allowed`: Optional whitelist of allowed group names
- `max-levels`: Maximum nesting levels (default: 3)
- `require-for-hidden`: Whether hidden fields need groups (default: false)

**Arguments**:

- `--config PATH`: Path to configuration file
- `--allowed-groups`: Comma-separated list of allowed group names

#### `check-naming-conventions`

**Purpose**: Enforce naming patterns for metrics and dimensions

**Validation Rules**:

1. **Pattern Validation**:

   - Metric names must match configured regex pattern
   - Dimension names must match configured regex pattern
   - Default patterns: `^[a-z][a-z0-9_]*$` (snake_case)

2. **Consistency Checks**:
   - Check for duplicate metric/dimension names across models
   - Validate label consistency with naming conventions

**Configuration Schema**:

- `metrics.pattern`: Regex pattern for metric names
- `metrics.max-length`: Maximum metric name length
- `dimensions.pattern`: Regex pattern for dimension names
- `dimensions.max-length`: Maximum dimension name length
- `additional-dimensions.pattern`: Regex pattern for additional dimensions

#### `check-descriptions`

**Purpose**: Validate description quality and completeness

**Validation Rules**:

1. **Completeness**:

   - All metrics must have descriptions (configurable)
   - All non-hidden dimensions must have descriptions
   - Model-level descriptions required

2. **Quality Checks**:
   - Minimum description length (default: 10 characters)
   - No placeholder text ("TODO", "TBD", etc.)
   - No duplicate descriptions across similar metrics

**Arguments**:

- `--min-length N`: Minimum description length
- `--require-model-desc`: Require model-level descriptions
- `--forbidden-terms`: Comma-separated list of forbidden placeholder terms

### Advanced Validation Hooks

#### `check-metric-consistency`

**Purpose**: Validate business logic consistency in metrics

**Validation Rules**:

1. **Type Consistency**:

   - Validate metric types against allowed values
   - Check for logical inconsistencies in metric definitions
   - Ensure aggregation types are appropriate for metric type

2. **Reference Validation**:
   - Check that metric SQL uses proper field reference syntax
   - Validate required fields are present for specific metric types
   - Ensure percentile metrics include percentile parameter

#### `validate-spotlight-config`

**Purpose**: Validate Spotlight-specific configurations

**Validation Rules**:

1. **Visibility Settings**:

   - `visibility`: Must be "show" or "hide"
   - `categories`: Must be array of strings if present

2. **Requirements**:
   - Must have either `visibility` or `categories` field
   - Categories must be from approved list if configured

#### `check-lightdash-formatting`

**Purpose**: Ensure consistent YAML formatting for Lightdash configs

**Validation Rules**:

1. **Indentation**: Consistent 2-space indentation
2. **Order**: Standardized key ordering within meta blocks
3. **Spacing**: Consistent spacing around colons and arrays

### DBT Version Management Hooks

#### `check-dbt-version-consistency`

**Purpose**: Validate consistent dbt version usage across project

**Validation Rules**:

1. **Version Detection**: Auto-detect dbt version per file
2. **Consistency Check**: Warn about mixed version usage in project
3. **Migration Status**: Report files that need migration to newer format

**Arguments**:

- `--enforce-version`: Require specific dbt version format
- `--warn-mixed`: Warn about mixed dbt versions in project

#### `validate-dbt-migration`

**Purpose**: Validate correctness of dbt 1.9 to 1.10 migration

**Validation Rules**:

1. **Structure Validation**: Ensure proper `config` block nesting for v1.10+
2. **Content Preservation**: Verify no data loss during migration
3. **Syntax Compliance**: Check adherence to new dbt 1.10 format

**Arguments**:

- `--source-version`: Specify source dbt version (default: auto-detect)
- `--target-version`: Specify target dbt version (default: 1.10+)

## Configuration System

### Configuration File: `.lightdash-pre-commit.yaml`

The configuration supports:

- **Project settings**: Project directory, dbt version specification
- **Global settings**: Universal validation requirements
- **Naming conventions**: Patterns for metrics, dimensions, and additional dimensions
- **Group label settings**: Enforcement rules and allowed values
- **Description requirements**: Length and quality rules
- **Spotlight settings**: Category restrictions
- **Schema validation**: Version and custom schema path settings

## Implementation Architecture

### Core Components

1. **Version-Aware YAML Parser**: Handles both dbt 1.9 and 1.10+ schema formats
2. **Schema Validator**: Validates against appropriate Lightdash JSON schema version
3. **Configuration Parser**: Loads and validates hook configuration
4. **Hook Base Class**: Provides common validation infrastructure with version awareness

### Error Handling

#### Error Message Format

```text
ERROR: {file_path}:{line_number} - {error_code}: {message}
  Context: {yaml_path}
  Fix: {suggested_fix}
```

#### Error Codes

- `LD001`: Missing required field
- `LD002`: Invalid field value
- `LD003`: Naming convention violation
- `LD004`: Missing description
- `LD005`: Invalid group label
- `LD006`: Join validation error
- `LD007`: Schema validation error
- `LD008`: Business logic error

### File Discovery

The hooks automatically discover and validate:

1. `models/**/schema.yml`
2. `models/**/_schema.yml`
3. `models/**/schema.yaml`
4. Files matching pattern specified in `--files` argument

### Dependencies

#### Required Python Packages

- `jsonschema>=4.0.0`
- `pydantic>=1.8.0`
- `ruamel.yaml>=0.17.0`
- `click>=8.0.0`

## Testing Strategy

### Unit Tests

- Individual validation rule testing
- Configuration parsing tests
- Error message formatting tests

### Integration Tests

- End-to-end hook execution
- Multi-file validation scenarios
- Configuration override testing

### Test Data

- Sample Lightdash configurations (valid/invalid)
- Edge cases and error conditions
- Performance test with large schemas

## Performance Requirements

- Process 100+ model files in <5 seconds
- Memory usage <100MB for typical projects
- Incremental validation (only changed files)
- Parallel processing support for large projects
