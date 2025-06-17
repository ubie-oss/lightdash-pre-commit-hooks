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

import argparse
from typing import Dict, List, Optional, Sequence, Tuple

import yaml  # type: ignore[import-untyped]
from pydantic import ValidationError

from lightdash_pre_commit.models.lightdash_dbt_2_0 import LightdashV20


def find_duplicates(data: LightdashV20) -> List[str]:
    """Find duplicate names across metrics and dimensions in a Lightdash DBT 2.0 model."""
    all_names: Dict[str, List[Tuple[str, str]]] = {}  # Track names and their sources
    errors: List[str] = []

    # Check for metrics and dimensions defined at the model level
    if data.models:
        for model in data.models:
            model_name = model.name or "unknown_model"

            # Process model-level metrics
            if model.meta and model.meta.metrics:
                for metric_name in model.meta.metrics.keys():
                    if metric_name not in all_names:
                        all_names[metric_name] = []
                    all_names[metric_name].append((model_name, "model-level metric"))

            # Check for metrics and dimensions defined at the column level
            if model.columns:
                for column in model.columns:
                    if not column.meta or not column.name:
                        continue

                    column_name = column.name

                    # Process column-level dimensions (the column name itself becomes a dimension)
                    if column.meta.dimension:
                        if column_name not in all_names:
                            all_names[column_name] = []
                        all_names[column_name].append(
                            (model_name, f"column '{column_name}' dimension")
                        )

                    # Process column-level additional dimensions
                    if column.meta.additional_dimensions:
                        for ad_dim_name in column.meta.additional_dimensions.keys():
                            if ad_dim_name not in all_names:
                                all_names[ad_dim_name] = []
                            all_names[ad_dim_name].append(
                                (
                                    model_name,
                                    f"additional dimension in column '{column_name}'",
                                )
                            )

                    # Process column-level metrics
                    if column.meta.metrics:
                        for metric_name in column.meta.metrics.keys():
                            if metric_name not in all_names:
                                all_names[metric_name] = []
                            all_names[metric_name].append(
                                (model_name, f"metric in column '{column_name}'")
                            )

    # Check for duplicates and gather detailed error messages
    for name, sources in all_names.items():
        if len(sources) > 1:
            source_descriptions = []
            for model_name, source_type in sources:
                source_descriptions.append(f"{source_type} in model '{model_name}'")

            errors.append(
                f"Duplicate name '{name}' used {len(sources)} times: {', '.join(source_descriptions)}"
            )

    return errors


def check_validation_errors(file_path: str, raw_data: dict) -> Optional[str]:
    """Check for validation errors when parsing YAML data with Pydantic model."""
    try:
        LightdashV20.model_validate(raw_data)
        return None
    except ValidationError as ve:
        return f"Validation error in '{file_path}': {ve}"


def process_single_file(file_path: str) -> Tuple[List[str], bool]:
    """Process a single file and return errors and success status."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            raw_data = yaml.safe_load(file)

            # Skip empty or None data
            if not raw_data:
                return [], True

            # Parse the YAML data using the Pydantic model
            validation_error = check_validation_errors(file_path, raw_data)
            if validation_error:
                return [validation_error], False

            lightdash_data = LightdashV20.model_validate(raw_data)
            duplicate_errors = find_duplicates(lightdash_data)

            return duplicate_errors, len(duplicate_errors) == 0

    except (FileNotFoundError, yaml.YAMLError, OSError) as e:
        return [f"Failed to process '{file_path}': {e}"], False


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check for duplicate metric and dimension names in Lightdash DBT 2.0 schema files"
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to check")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information about checked files",
    )
    args = parser.parse_args(argv)

    if not args.filenames:
        print("No files provided to check.")
        return 0

    error_flag = False
    total_files = len(args.filenames)
    processed_files = 0

    for file_path in args.filenames:
        errors, _ = process_single_file(file_path)
        processed_files += 1

        if errors:
            print(f"Errors found in '{file_path}':")
            for error in errors:
                print(f"  {error}")
            error_flag = True
        elif args.verbose:
            print(f"✓ No duplicates found in '{file_path}'")

    if args.verbose:
        print(f"\nProcessed {processed_files}/{total_files} files.")
        if not error_flag:
            print("All files passed duplicate checks!")

    return 1 if error_flag else 0


if __name__ == "__main__":
    exit(main(None))
