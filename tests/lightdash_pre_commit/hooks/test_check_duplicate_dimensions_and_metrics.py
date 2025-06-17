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

import os
import unittest

import yaml  # type: ignore[import-untyped]

from lightdash_pre_commit.hooks.check_duplicate_dimensions_and_metrics import (
    find_duplicates,
)
from lightdash_pre_commit.models.lightdash_dbt_2_0 import LightdashV20


class TestCheckDuplicateDimensionsAndMetrics(unittest.TestCase):
    """Test the check_duplicate_dimensions_and_metrics hook."""

    def setUp(self):
        """Set up the fixture directory path."""
        self.fixtures_dir = os.path.join(
            os.path.dirname(__file__),
            "fixtures",
            "check_duplicate_dimensions_and_metrics",
        )

    def _load_fixture(self, filename: str) -> dict:
        """Load a YAML fixture file and return the parsed data."""
        fixture_path = os.path.join(self.fixtures_dir, filename)
        with open(fixture_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def _get_lightdash_data(self, filename: str) -> LightdashV20:
        """Load a fixture and convert it to LightdashV20 model."""
        raw_data = self._load_fixture(filename)
        return LightdashV20.model_validate(raw_data)

    def test_no_metrics_or_dimensions(self):
        """Test with empty models - should return no errors."""
        lightdash_data = self._get_lightdash_data("empty_model.yml")
        errors = find_duplicates(lightdash_data)
        self.assertEqual(errors, [])

    def test_unique_metric_and_dimension_names(self):
        """Test with unique metric and dimension names - should return no errors."""
        lightdash_data = self._get_lightdash_data("unique_names.yml")
        errors = find_duplicates(lightdash_data)
        self.assertEqual(errors, [])

    def test_duplicate_name_across_metric_and_dimension(self):
        """Test duplicate name between model-level metric and column-level metric."""
        lightdash_data = self._get_lightdash_data(
            "duplicate_across_metric_and_dimension.yml"
        )
        errors = find_duplicates(lightdash_data)

        # Check that we found the duplicate
        self.assertEqual(len(errors), 1)
        error_msg = errors[0]
        self.assertIn("Duplicate name 'revenue_total' used 2 times:", error_msg)
        self.assertIn("model-level metric", error_msg)
        self.assertIn("metric in column 'revenue'", error_msg)

    def test_duplicate_within_metrics(self):
        """Test duplicate metric names across different columns."""
        lightdash_data = self._get_lightdash_data("duplicate_within_metrics.yml")
        errors = find_duplicates(lightdash_data)

        # Check that we found the duplicate
        self.assertEqual(len(errors), 1)
        error_msg = errors[0]
        self.assertIn("Duplicate name 'test_me' used 2 times:", error_msg)
        self.assertIn("metric in column 'date_at'", error_msg)
        self.assertIn("metric in column 'revenue'", error_msg)

    def test_duplicate_within_dimensions(self):
        """Test duplicate dimension names in additional_dimensions across columns."""
        lightdash_data = self._get_lightdash_data("duplicate_within_dimensions.yml")
        errors = find_duplicates(lightdash_data)

        # Check that we found the duplicate
        self.assertEqual(len(errors), 1)
        error_msg = errors[0]
        self.assertIn("Duplicate name 'test_me' used 2 times:", error_msg)
        self.assertIn("additional dimension in column 'date_at'", error_msg)
        self.assertIn("additional dimension in column 'revenue'", error_msg)

    def test_duplicate_between_column_dimension_and_additional_dimension(self):
        """Test duplicate between column name (dimension) and additional_dimension."""
        lightdash_data = self._get_lightdash_data(
            "duplicate_column_vs_additional_dimension.yml"
        )
        errors = find_duplicates(lightdash_data)

        # Check that we found the duplicate
        self.assertEqual(len(errors), 1)
        error_msg = errors[0]
        self.assertIn("Duplicate name 'user_id' used 2 times:", error_msg)
        self.assertIn("column 'user_id' dimension", error_msg)
        self.assertIn("additional dimension in column 'user_id'", error_msg)

    def test_duplicate_between_metric_and_additional_dimension(self):
        """Test duplicate between metric and additional_dimension names."""
        lightdash_data = self._get_lightdash_data(
            "duplicate_metric_vs_additional_dimension.yml"
        )
        errors = find_duplicates(lightdash_data)

        # Check that we found the duplicate
        self.assertEqual(len(errors), 1)
        error_msg = errors[0]
        self.assertIn("Duplicate name 'revenue_sum' used 2 times:", error_msg)
        self.assertIn("metric in column 'revenue'", error_msg)
        self.assertIn("additional dimension in column 'revenue'", error_msg)

    def test_multiple_duplicates(self):
        """Test with multiple different duplicates in the same model."""
        lightdash_data = self._get_lightdash_data("multiple_duplicates.yml")
        errors = find_duplicates(lightdash_data)

        # Should find multiple duplicates
        self.assertTrue(len(errors) >= 2)
        error_text = " ".join(errors)
        self.assertIn("total_count", error_text)
        self.assertIn("user_metric", error_text)
        self.assertIn("user_id", error_text)

    def test_no_meta_columns(self):
        """Test with columns that have no meta section."""
        lightdash_data = self._get_lightdash_data("no_meta_columns.yml")
        errors = find_duplicates(lightdash_data)
        self.assertEqual(errors, [])

    def test_mixed_meta_and_no_meta_columns(self):
        """Test with a mix of columns with and without meta sections."""
        lightdash_data = self._get_lightdash_data("mixed_meta_columns.yml")
        errors = find_duplicates(lightdash_data)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
