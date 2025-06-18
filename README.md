# Lightdash pre-commit hooks

This is a collection of pre-commit hooks for Lightdash.

## Set up pre-commit hooks

Add the following to your `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/ubie-oss/lightdash-pre-commit-hooks
    rev: <latest-version>
    hooks:
      - id: check-duplicate-dimensions-and-metrics-v1
```

## Pre-commit hooks

### `check-duplicate-dimensions-and-metrics-v1`

This hook checks for duplicate dimensions and metrics in the dbt schema file for dbt 1.9 or earlier.

### `check-duplicate-dimensions-and-metrics-v2`

This hook checks for duplicate dimensions and metrics in the dbt schema file for dbt 1.10 or later.
