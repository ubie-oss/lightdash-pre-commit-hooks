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
from lightdash_pre_commit.parsers.lightdash_dbt_2_5 import LightdashV25, Models


class FindDuplicateDimensionsAndMetricsV2(BaseChecker):
    """Find duplicate names across metrics and dimensions for dbt 1.10 or later."""

    @classmethod
    def check(cls, data: LightdashV25) -> List[str]:  # type: ignore[override]
        """Check the data and return a list of errors."""
        if not isinstance(data, LightdashV25):
            raise ValueError("Expected 'data' keyword argument of type LightdashV25")

        all_names: Dict[str, List[Tuple[str, str]]] = (
            {}
        )  # Track names and their sources
        errors: List[str] = []

        # Check for metrics and dimensions defined at the model level
        if data.models:
            for model in data.models:
                model_name = model.name or "unknown_model"

                # Process model-level metrics (handle both old and new formats)
                model_meta = None
                if hasattr(model, "meta") and model.meta:
                    model_meta = model.meta
                elif hasattr(model, "config") and model.config and model.config.meta:
                    model_meta = model.config.meta

                if model_meta and model_meta.metrics:
                    for metric_name in model_meta.metrics.keys():
                        if metric_name not in all_names:
                            all_names[metric_name] = []
                        all_names[metric_name].append(
                            (model_name, "model-level metric")
                        )

                # Check for metrics and dimensions defined at the column level
                if model.columns:
                    for column in model.columns:
                        if not column.name:
                            continue

                        column_name = column.name

                        # Get column meta (handle both old and new formats)
                        column_meta = None
                        if hasattr(column, "meta") and column.meta:
                            column_meta = column.meta
                        elif (
                            hasattr(column, "config")
                            and column.config
                            and column.config.meta
                        ):
                            column_meta = column.config.meta

                        if not column_meta:
                            continue

                        # Process column-level dimensions (the column name itself becomes a dimension)
                        if column_meta.dimension:
                            if column_name not in all_names:
                                all_names[column_name] = []
                            all_names[column_name].append(
                                (model_name, f"column '{column_name}' dimension")
                            )

                        # Process column-level additional dimensions
                        if column_meta.additional_dimensions:
                            for ad_dim_name in column_meta.additional_dimensions.keys():
                                if ad_dim_name not in all_names:
                                    all_names[ad_dim_name] = []
                                all_names[ad_dim_name].append(
                                    (
                                        model_name,
                                        f"additional dimension in column '{column_name}'",
                                    )
                                )

                        # Process column-level metrics
                        if column_meta.metrics:
                            for metric_name in column_meta.metrics.keys():
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
    def find_duplicates_dimensions(cls, model: Models) -> List[str]:
        """Find duplicate names within dimensions in a Lightdash DBT 2.5 model."""
        dimension_names: Dict[str, List[str]] = (
            {}
        )  # Track dimension names and their sources
        errors: List[str] = []
        model_name = model.name or "unknown_model"

        # Check for dimensions defined at the column level
        if model.columns:
            for column in model.columns:
                if not column.config or not column.config.meta or not column.name:
                    continue

                column_name = column.name

                # Process column-level dimensions (the column name itself becomes a dimension)
                if column.config.meta.dimension:
                    if column_name not in dimension_names:
                        dimension_names[column_name] = []
                    dimension_names[column_name].append(
                        f"column '{column_name}' dimension"
                    )

                # Process column-level additional dimensions
                if column.config.meta.additional_dimensions:
                    for ad_dim_name in column.config.meta.additional_dimensions.keys():
                        if ad_dim_name not in dimension_names:
                            dimension_names[ad_dim_name] = []
                        dimension_names[ad_dim_name].append(
                            f"additional dimension in column '{column_name}'"
                        )

        # Check for duplicates within dimensions
        for name, sources in dimension_names.items():
            if len(sources) > 1:
                # pylint: disable=line-too-long
                errors.append(
                    f"Duplicate dimension name '{name}' used {len(sources)} times in model '{model_name}': {', '.join(sources)}"
                )

        return errors

    @classmethod
    def find_duplicates_metrics(cls, model: Models) -> List[str]:
        """Find duplicate names within metrics in a Lightdash DBT 2.5 model."""
        metric_names: Dict[str, List[str]] = {}  # Track metric names and their sources
        errors: List[str] = []
        model_name = model.name or "unknown_model"

        # Process model-level metrics
        if model.config and model.config.meta and model.config.meta.metrics:
            for metric_name in model.config.meta.metrics.keys():
                if metric_name not in metric_names:
                    metric_names[metric_name] = []
                metric_names[metric_name].append("model-level metric")

        # Check for metrics defined at the column level
        if model.columns:
            for column in model.columns:
                if not column.config or not column.config.meta or not column.name:
                    continue

                column_name = column.name

                # Process column-level metrics
                if column.config.meta.metrics:
                    for metric_name in column.config.meta.metrics.keys():
                        if metric_name not in metric_names:
                            metric_names[metric_name] = []
                        metric_names[metric_name].append(
                            f"metric in column '{column_name}'"
                        )

        # Check for duplicates within metrics
        for name, sources in metric_names.items():
            if len(sources) > 1:
                # pylint: disable=line-too-long
                errors.append(
                    f"Duplicate metric name '{name}' used {len(sources)} times in model '{model_name}': {', '.join(sources)}"
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
