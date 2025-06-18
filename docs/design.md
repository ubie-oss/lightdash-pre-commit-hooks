# Lightdash Pre-commit Hooks - Technical Specification

## Overview

This specification defines a lightweight set of pre-commit hooks for validating Lightdash-specific configurations in dbt schema files. The hooks operate by parsing YAML files directly and validating the `meta` sections that contain Lightdash configurations, without requiring dbt-core or a full dbt environment.

## Why These Hooks Matter

### The Problem We Solve

Teams using Lightdash often struggle with:

- **Inconsistent metric definitions** across models leading to confusion
- **Missing or poor descriptions** making dashboards hard to understand
- **Schema validation errors** discovered only during deployment
- **Naming convention drift** as teams grow and add more models
- **Broken joins and references** that cause runtime errors
- **Technical debt accumulation** in Lightdash configurations

### The Solution: Great Pre-commit Hooks

Our hooks provide:

#### 🚀 **Instant Feedback**

- Catch issues before they reach your repository
- Fix problems in seconds, not hours
- No more "it works on my machine" scenarios

#### 📊 **Better Data Quality**

- Enforce consistent metric definitions
- Require meaningful descriptions
- Validate business logic early

#### 🏗️ **Team Scalability**

- Consistent standards across all team members
- Onboard new developers faster
- Reduce code review overhead

#### ⚡ **Developer Experience**

- Fast validation (< 5 seconds for 100+ models)
- Clear, actionable error messages
- Zero configuration to get started

## Hook Gallery: Your Lightdash Quality Toolkit

### 🔍 **Schema Validation** - `validate-lightdash-schema`

**What it does**: Validates all Lightdash configurations against the official JSON schema

**Why you need it**: Prevents deployment failures and ensures your configurations work in production

**Example validation**:

```yaml
# ❌ This will fail
models:
  - name: orders
    meta:
      metrics:
        - name: total_revenue
          type: "invalid_type"  # Not in allowed types

# ✅ This will pass
models:
  - name: orders
    meta:
      metrics:
        - name: total_revenue
          type: "sum"
          sql: "amount"
```

**Perfect for**: Teams starting with Lightdash, preventing basic configuration errors

### 📏 **Metric Quality** - `check-metric-definitions`

**What it does**: Ensures all metrics have proper types, SQL, and optional fields

**Why you need it**: Prevents broken dashboards and ensures metrics are well-defined

**Example validation**:

```yaml
# ❌ Missing required SQL
metrics:
  - name: order_count
    type: "count_distinct"
    # Missing sql field

# ✅ Complete metric definition
metrics:
  - name: order_count
    type: "count_distinct"
    sql: "order_id"
    label: "Total Orders"
    description: "Count of unique orders in the system"
```

**Perfect for**: Analytics teams who want reliable metrics

### 🏷️ **Naming Standards** - `check-naming-conventions`

**What it does**: Enforces consistent naming patterns across all metrics and dimensions

**Why you need it**: Makes your Lightdash dashboards predictable and professional

**Example validation**:

```yaml
# ❌ Inconsistent naming
metrics:
  - name: "Total Revenue"      # Space in name
  - name: "order-count"        # Kebab case
  - name: "userCount"          # Camel case

# ✅ Consistent snake_case
metrics:
  - name: "total_revenue"
  - name: "order_count"
  - name: "user_count"
```

**Perfect for**: Teams with multiple developers, maintaining professional standards

### 📝 **Description Quality** - `check-descriptions`

**What it does**: Ensures all metrics and dimensions have meaningful descriptions

**Why you need it**: Makes dashboards self-documenting and user-friendly

**Example validation**:

```yaml
# ❌ Poor descriptions
metrics:
  - name: revenue
    description: "Revenue"  # Too short, not helpful

# ✅ Great descriptions
metrics:
  - name: revenue
    description: "Total revenue in USD from completed orders, excluding taxes and discounts"
```

**Perfect for**: Customer-facing dashboards, reducing support requests

### 🔗 **Join Validation** - `validate-joins`

**What it does**: Validates join syntax and field references

**Why you need it**: Prevents broken relationships between models

**Example validation**:

```yaml
# ❌ Invalid join syntax
meta:
  joins:
    - join: customers
      sql_on: "orders.customer_id = customer.id"  # Wrong reference syntax

# ✅ Correct Lightdash syntax
meta:
  joins:
    - join: customers
      sql_on: "${orders.customer_id} = ${customers.id}"
```

**Perfect for**: Complex data models with multiple table relationships

### 🏢 **Organization** - `check-group-labels`

**What it does**: Enforces consistent grouping and categorization

**Why you need it**: Makes large dashboards navigable and organized

**Example validation**:

```yaml
# ❌ Inconsistent grouping
metrics:
  - name: revenue
    groups: ["sales", "Revenue"]  # Inconsistent casing
  - name: orders
    groups: ["Sales", "orders", "metrics", "kpis"]  # Too many levels

# ✅ Consistent organization
metrics:
  - name: revenue
    groups: ["Sales", "Revenue"]
  - name: orders
    groups: ["Sales", "Orders"]
```

**Perfect for**: Large organizations with many metrics and dimensions

## Progressive Adoption Strategy

### Phase 1: Start Simple (Week 1)

```yaml
repos:
  - repo: https://github.com/lightdash/lightdash-pre-commit-hooks
    rev: v1.0.0
    hooks:
      - id: validate-lightdash-schema # Just basic validation
```

### Phase 2: Add Quality (Week 2-3)

```yaml
repos:
  - repo: https://github.com/lightdash/lightdash-pre-commit-hooks
    rev: v1.0.0
    hooks:
      - id: validate-lightdash-schema
      - id: check-metric-definitions
      - id: check-descriptions
        args: ["--min-length=15"]
```

### Phase 3: Full Quality Suite (Month 2)

```yaml
repos:
  - repo: https://github.com/lightdash/lightdash-pre-commit-hooks
    rev: v1.0.0
    hooks:
      - id: validate-lightdash-schema
      - id: check-metric-definitions
        args: ["--require-description", "--require-labels"]
      - id: check-dimension-definitions
      - id: check-descriptions
        args: ["--min-length=20", "--require-model-desc"]
      - id: check-naming-conventions
      - id: validate-joins
      - id: check-group-labels
```

## Configuration Examples

### Basic Team Configuration (`.lightdash-pre-commit.yaml`)

```yaml
# Perfect for small teams getting started
project:
  dbt_version: "1.10+"

naming_conventions:
  metrics:
    pattern: "^[a-z][a-z0-9_]*$"
    max_length: 50
  dimensions:
    pattern: "^[a-z][a-z0-9_]*$"
    max_length: 50

descriptions:
  min_length: 15
  require_model_descriptions: true
  forbidden_terms: ["TODO", "TBD", "placeholder"]
```

### Enterprise Configuration

```yaml
# For large organizations with strict standards
project:
  dbt_version: "1.10+"

naming_conventions:
  metrics:
    pattern: "^(count|sum|avg|min|max|ratio)_[a-z][a-z0-9_]*$"
    max_length: 60
  dimensions:
    pattern: "^[a-z][a-z0-9_]*(_dim)?$"
    max_length: 50

group_labels:
  enforce: true
  max_levels: 3
  allowed:
    - "Sales"
    - "Marketing"
    - "Finance"
    - "Operations"
    - "Customer Success"

descriptions:
  min_length: 25
  require_model_descriptions: true
  require_metric_descriptions: true
  forbidden_terms: ["TODO", "TBD", "placeholder", "temp", "test"]

spotlight:
  allowed_categories:
    - "KPI"
    - "Operational"
    - "Exploratory"
    - "Debug"
```

## Integration Best Practices

### With CI/CD Pipelines

```yaml
# .github/workflows/lightdash-quality.yml
name: Lightdash Quality Check
on: [push, pull_request]

jobs:
  lightdash-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      - name: Install pre-commit
        run: pip install pre-commit
      - name: Run Lightdash hooks
        run: pre-commit run --all-files --hook-stage manual
```

### With dbt Cloud

```yaml
# dbt_project.yml - Add validation to your dbt runs
pre-hook: |
  {{ log("Running Lightdash validation...") }}
  {% if execute %}
    {% set result = run_command("pre-commit run validate-lightdash-schema --files " ~ this.path) %}
    {{ log("Validation result: " ~ result) }}
  {% endif %}
```

### Team Workflow Integration

1. **Developer Setup** (5 minutes):

   ```bash
   # One-time setup per developer
   pip install pre-commit
   pre-commit install
   ```

2. **Daily Development**:

   - Hooks run automatically on `git commit`
   - Instant feedback on Lightdash configurations
   - Fix issues before pushing code

3. **Code Reviews**:
   - Reviewers focus on business logic
   - No more syntax or formatting discussions
   - Consistent quality across all PRs

## Advanced Features

### Smart Error Messages

```text
❌ ERROR: models/marts/orders.yml:15 - LD002: Invalid metric type
  Context: meta.metrics[0].type = "invalid_sum"
  Expected: One of [sum, count, average, min, max, count_distinct, percentile, median, boolean, date, number, string]
  Fix: Change "invalid_sum" to "sum"

💡 TIP: Most aggregation metrics use "sum", "count", or "average"
```

### Performance Optimization

- **Incremental validation**: Only check changed files
- **Parallel processing**: Validate multiple files simultaneously
- **Smart caching**: Skip unchanged configurations
- **Fast-fail mode**: Stop on first error for rapid iteration

### IDE Integration

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "files.associations": {
    "**/schema.yml": "yaml",
    "**/_schema.yml": "yaml"
  },
  "yaml.schemas": {
    "./resources/schemas/lightdash-dbt-2.0.json": [
      "**/schema.yml",
      "**/_schema.yml"
    ]
  }
}
```

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

**Features**:

- **JSON Schema validation**: Validates YAML structure against Lightdash schema
- **Custom schema paths**: Support for custom schema file locations
- **Clear error reporting**: Shows exact YAML path and expected values
- **Fast YAML parsing**: Only processes files with Lightdash `meta` sections

**Requirements**:

- Must validate against `lightdash-dbt-2.0.json` schema
- Support for custom schema file paths via `--schema-path` argument
- Validate nested structures: `meta.metrics`, `meta.dimension`, `meta.joins`

**Arguments**:

- `--schema-path`: Path to Lightdash schema file (default: uses bundled schema)
- `--model-filter`: Regex pattern to filter specific models
- `--strict-mode`: Fail on warnings, not just errors

**Example error output**:

```text
❌ ERROR: models/marts/orders.yml:12 - LD007: Schema validation error
  Context: meta.metrics[0].type
  Current value: "invalid_sum"
  Expected: One of ["sum", "count", "average", "min", "max", "count_distinct", "percentile", "median", "boolean", "date", "number", "string"]

💡 TIP: Use "sum" for additive metrics like revenue, quantity, etc.
📖 Docs: https://docs.lightdash.com/references/metrics#metric-types
```

**Exit codes**:

- `0`: All validations pass
- `1`: Schema validation failures found
- `2`: Configuration or setup errors

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
   - `percentile`: Must be number between 0-100 if type is `percentile`

3. **Business Logic**:
   - `percentile` field required when type is `percentile`
   - `sql` field optional when type is `count`

**Example validation**:

```yaml
# ❌ This will fail
metrics:
  - name: avg_order_value
    type: "invalid_type"  # Not in allowed types
    sql: ""  # Empty SQL not allowed

# ✅ This will pass
metrics:
  - name: avg_order_value
    type: "average"
    sql: "amount"
    label: "Average Order Value"
    description: "Mean order value calculated from completed orders"
    round: 2
```

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

**Example validation**:

```yaml
# ❌ This will fail
dimensions:
  - name: created_date
    type: "invalid_type"  # Not in allowed types
    time_intervals: ["INVALID_INTERVAL"]  # Invalid interval

# ✅ This will pass
dimensions:
  - name: created_date
    type: "date"
    sql: "DATE(created_at)"
    time_intervals: ["DAY", "WEEK", "MONTH", "QUARTER", "YEAR"]
```

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

**Example validation**:

```yaml
# ❌ This will fail
meta:
  joins:
    - join: customers
      sql_on: "orders.customer_id = customer.id"  # Wrong reference syntax

# ✅ This will pass
meta:
  joins:
    - join: customers
      sql_on: "${orders.customer_id} = ${customers.id}"
```

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

#### `check-duplicate-dimensions-and-metrics`

**Purpose**: Detect and prevent duplicate metric and dimension names within models and across models

**Why you need it**: Prevents confusing dashboards where multiple fields have the same name but different definitions

**Validation Rules**:

1. **Within Model Duplicates**:

   - No duplicate names within `meta.metrics[]`
   - No duplicate names within `meta.dimensions[]`
   - No overlap between metric names and dimension names
   - No overlap between regular dimensions and `additional_dimensions[]`

2. **Cross-Model Duplicates** (optional):

   - Detect same metric/dimension names across different models
   - Configurable to allow or warn about cross-model duplicates

3. **Case Sensitivity**:
   - Consider `revenue` and `Revenue` as duplicates
   - Detect common typos and similar names

**Example validation**:

```yaml
# ❌ This will fail - duplicate metrics
models:
  - name: orders
    meta:
      metrics:
        - name: total_revenue
          type: sum
          sql: amount
        - name: total_revenue  # Duplicate!
          type: sum
          sql: gross_amount

# ❌ This will fail - metric/dimension overlap
models:
  - name: orders
    meta:
      metrics:
        - name: customer_id
          type: count_distinct
          sql: customer_id
      dimensions:
        - name: customer_id  # Conflicts with metric!
          type: string

# ✅ This will pass - unique names
models:
  - name: orders
    meta:
      metrics:
        - name: total_revenue
          type: sum
          sql: amount
        - name: customer_count
          type: count_distinct
          sql: customer_id
      dimensions:
        - name: customer_id
          type: string
        - name: order_date
          type: date
```

**Arguments**:

- `--check-cross-model`: Enable cross-model duplicate detection (default: false)
- `--case-sensitive`: Treat different cases as different names (default: false)
- `--similarity-threshold`: Detect similar names that might be typos (default: 0.8)
- `--exclude-models`: Regex pattern for models to exclude from cross-model checks

**Configuration**:

```yaml
# .lightdash-pre-commit.yaml
duplicate_detection:
  cross_model_check: true
  case_sensitive: false
  similarity_threshold: 0.85
  exclude_patterns:
    - "staging_*"
    - "*_test"
  allowed_duplicates:
    - "id" # Allow 'id' across models
    - "created_at"
```

**Perfect for**: Preventing naming conflicts that confuse dashboard users

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
