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
from typing import Dict, List, Optional, Sequence

from lightdash_pre_commit.hooks.base import BaseChecker
from lightdash_pre_commit.hooks.utils import process_single_file
from lightdash_pre_commit.parsers.lightdash_dbt_2_5 import LightdashV25


class FindDuplicateDimensionsAndMetricsV2(BaseChecker):
    """Find duplicate names across metrics and dimensions for dbt 1.10 or later."""

    @classmethod
    def check(cls, data: LightdashV25) -> List[str]:  # type: ignore[override]
        """Check the data and return a list of errors."""
        if not isinstance(data, LightdashV25):
            raise ValueError("Expected 'data' keyword argument of type LightdashV25")

        all_errors: List[str] = []

        # Check for duplicates within each model individually
        if data.models:
            for model in data.models:
                model_name = model.name or "unknown_model"
                model_errors = cls._check_single_model(model, model_name)
                all_errors.extend(model_errors)

        return all_errors

    @classmethod
    def _check_single_model(cls, model, model_name: str) -> List[str]:
        """Check for duplicates within a single model."""
        all_names: Dict[str, List[str]] = {}  # Track names and their sources
        errors: List[str] = []

        # Get model-level meta (handle different model types)
        model_meta = None
        if hasattr(model, "meta") and model.meta:
            model_meta = model.meta
        elif (
            hasattr(model, "config")
            and model.config
            and hasattr(model.config, "meta")
            and model.config.meta
        ):
            model_meta = model.config.meta

        # Process model-level metrics
        if model_meta and hasattr(model_meta, "metrics") and model_meta.metrics:
            for metric_name in model_meta.metrics.keys():
                if metric_name not in all_names:
                    all_names[metric_name] = []
                all_names[metric_name].append("model-level metric")

        # Check for metrics and dimensions defined at the column level
        if hasattr(model, "columns") and model.columns:
            for column in model.columns:
                if not hasattr(column, "name") or not column.name:
                    continue

                column_name = column.name

                # Get column meta (handle different column types)
                column_meta = None
                if hasattr(column, "meta") and column.meta:
                    column_meta = column.meta
                elif (
                    hasattr(column, "config")
                    and column.config
                    and hasattr(column.config, "meta")
                    and column.config.meta
                ):
                    column_meta = column.config.meta

                if not column_meta:
                    continue

                # Process column-level dimensions (the column name itself becomes a dimension)
                if hasattr(column_meta, "dimension") and column_meta.dimension:
                    if column_name not in all_names:
                        all_names[column_name] = []
                    all_names[column_name].append(f"column '{column_name}' dimension")

                # Process column-level additional dimensions
                if (
                    hasattr(column_meta, "additional_dimensions")
                    and column_meta.additional_dimensions
                ):
                    for ad_dim_name in column_meta.additional_dimensions.keys():
                        if ad_dim_name not in all_names:
                            all_names[ad_dim_name] = []
                        all_names[ad_dim_name].append(
                            f"additional dimension in column '{column_name}'"
                        )

                # Process column-level metrics
                if hasattr(column_meta, "metrics") and column_meta.metrics:
                    for metric_name in column_meta.metrics.keys():
                        if metric_name not in all_names:
                            all_names[metric_name] = []
                        all_names[metric_name].append(
                            f"metric in column '{column_name}'"
                        )

        # Check for duplicates within this model
        for name, sources in all_names.items():
            if len(sources) > 1:
                errors.append(
                    f"Duplicate name '{name}' used {len(sources)} times: {', '.join(sources)} in model '{model_name}'"
                )

        return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point for the hook."""
    parser = argparse.ArgumentParser(
        description="Check for duplicate dimensions and metrics in Lightdash DBT files"
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to check")
    args = parser.parse_args(argv)

    if not args.filenames:
        print("No files provided.")
        return 0

    exit_code = 0
    for file_path in args.filenames:
        errors, success = process_single_file(
            file_path, LightdashV25, FindDuplicateDimensionsAndMetricsV2
        )
        if not success:
            exit_code = 1
        for error in errors:
            print(error)

    return exit_code


if __name__ == "__main__":
    exit(main())
