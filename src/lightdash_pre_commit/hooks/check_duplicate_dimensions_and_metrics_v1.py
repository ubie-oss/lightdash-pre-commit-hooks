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

from lightdash_pre_commit.hooks.base import BaseChecker
from lightdash_pre_commit.hooks.utils import process_single_file
from lightdash_pre_commit.parsers.lightdash_dbt_2_0 import LightdashV20, Model


class FindDuplicateDimensionsAndMetricsV1(BaseChecker):
    """Find duplicate names across metrics and dimensions for dbt 1.9 or earlier."""

    @classmethod
    def check(cls, data: LightdashV20) -> List[str]:  # type: ignore[override]
        """Check the data and return a list of errors."""
        if not isinstance(data, LightdashV20):
            raise ValueError("Expected 'data' keyword argument of type LightdashV20")

        all_names: Dict[str, List[Tuple[str, str]]] = (
            {}
        )  # Track names and their sources
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
                        all_names[metric_name].append(
                            (model_name, "model-level metric")
                        )

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

    @classmethod
    def find_duplicates_dimensions(cls, model: Model) -> List[str]:
        """Find duplicate names within dimensions in a Lightdash DBT 2.0 model."""
        dimension_names: Dict[str, List[str]] = (
            {}
        )  # Track dimension names and their sources
        errors: List[str] = []
        model_name = model.name or "unknown_model"

        # Check for dimensions defined at the column level
        if model.columns:
            for column in model.columns:
                if not column.meta or not column.name:
                    continue

                column_name = column.name

                # Process column-level dimensions (the column name itself becomes a dimension)
                if column.meta.dimension:
                    if column_name not in dimension_names:
                        dimension_names[column_name] = []
                    dimension_names[column_name].append(
                        f"column '{column_name}' dimension"
                    )

                # Process column-level additional dimensions
                if column.meta.additional_dimensions:
                    for ad_dim_name in column.meta.additional_dimensions.keys():
                        if ad_dim_name not in dimension_names:
                            dimension_names[ad_dim_name] = []
                        dimension_names[ad_dim_name].append(
                            f"additional dimension in column '{column_name}'"
                        )

        # Check for duplicates within dimensions
        for name, sources in dimension_names.items():
            if len(sources) > 1:
                errors.append(
                    f"Duplicate dimension name '{name}' used {len(sources)} times "
                    f"in model '{model_name}': {', '.join(sources)}"
                )

        return errors

    @classmethod
    def find_duplicates_metrics(cls, model: Model) -> List[str]:
        """Find duplicate names within metrics in a Lightdash DBT 2.0 model."""
        metric_names: Dict[str, List[str]] = {}  # Track metric names and their sources
        errors: List[str] = []
        model_name = model.name or "unknown_model"

        # Process model-level metrics
        if model.meta and model.meta.metrics:
            for metric_name in model.meta.metrics.keys():
                if metric_name not in metric_names:
                    metric_names[metric_name] = []
                metric_names[metric_name].append("model-level metric")

        # Check for metrics defined at the column level
        if model.columns:
            for column in model.columns:
                if not column.meta or not column.name:
                    continue

                column_name = column.name

                # Process column-level metrics
                if column.meta.metrics:
                    for metric_name in column.meta.metrics.keys():
                        if metric_name not in metric_names:
                            metric_names[metric_name] = []
                        metric_names[metric_name].append(
                            f"metric in column '{column_name}'"
                        )

        # Check for duplicates within metrics
        for name, sources in metric_names.items():
            if len(sources) > 1:
                errors.append(
                    f"Duplicate metric name '{name}' used {len(sources)} times "
                    f"in model '{model_name}': {', '.join(sources)}"
                )

        return errors


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
        errors, _ = process_single_file(
            file_path, LightdashV20, FindDuplicateDimensionsAndMetricsV1
        )
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
