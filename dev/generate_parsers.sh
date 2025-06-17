#!/bin/bash
set -Eeuo pipefail

# Constants
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "${SCRIPT_PATH}")"
MODULE_ROOT="$(dirname "${SCRIPT_DIR}")"

# Base class
base_class="lightdash_pre_commit.models.base.BaseParserModel"
target_python_version="3.10"
output_model_type="pydantic_v2.BaseModel"

# Generate LightdashV20 model
destination="${MODULE_ROOT}/src/lightdash_pre_commit/models/lightdash_dbt_2_0.py"
datamodel-codegen --input-file-type jsonschema \
	--target-python-version "${target_python_version}" \
	--output-model-type "${output_model_type}" \
	--disable-timestamp \
	--base-class "${base_class}" \
	--class-name "LightdashV20" \
	--input "${MODULE_ROOT}/resources/schemas/lightdash-dbt-2.0.json" \
	--output "${destination}" \
	--extra-fields ignore \
	--disable-timestamp \
	--reuse-model \
	--use-schema-description
