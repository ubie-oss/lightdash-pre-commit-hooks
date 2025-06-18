# Copyright 2025 Ubie, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Optional, Tuple, Type

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, ValidationError

from lightdash_pre_commit.hooks.base import BaseChecker


def check_validation_errors(
    file_path: str, raw_data: dict, validator_class: Type[BaseModel]
) -> Optional[str]:
    """Check for validation errors when parsing YAML data with Pydantic model."""
    try:
        validator_class.model_validate(raw_data)
        return None
    except ValidationError as ve:
        return f"Validation error in '{file_path}': {ve}"


def process_single_file(
    file_path: str,
    validator_class: Type[BaseModel],
    checker_class: Type[BaseChecker],
) -> Tuple[List[str], bool]:
    """Process a single file and return errors and success status.

    Args:
        file_path: Path to the file to process
        validator_class: Pydantic model class for validation (e.g., LightdashV20, LightdashV25)
        checker_class: Checker class for duplicate detection (e.g., FindDuplicateDimensionsAndMetricsV1)

    Returns:
        Tuple of (errors, success_status)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            raw_data = yaml.safe_load(file)

            # Skip empty or None data
            if not raw_data:
                return [], True

            # Parse the YAML data using the Pydantic model
            validation_error = check_validation_errors(
                file_path, raw_data, validator_class
            )
            if validation_error:
                return [validation_error], False

            lightdash_data = validator_class.model_validate(raw_data)
            # Use type: ignore to bypass type checker for this specific case
            duplicate_errors = checker_class.check(data=lightdash_data)  # type: ignore[arg-type]

            return duplicate_errors, len(duplicate_errors) == 0

    except (FileNotFoundError, yaml.YAMLError, OSError) as e:
        return [f"Failed to process '{file_path}': {e}"], False
