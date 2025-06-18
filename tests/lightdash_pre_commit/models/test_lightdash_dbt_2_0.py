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

# pylint: disable=unsubscriptable-object

import os
import unittest
from typing import cast

from lightdash_pre_commit.parsers.lightdash_dbt_2_0 import LightdashV20
from tests.lightdash_pre_commit.utils import get_test_root_dir, load_yaml


class TestLightdashV20(unittest.TestCase):
    """Test the LightdashV20 model."""

    def test_parse_simple_model_schema(self):
        path = os.path.join(
            get_test_root_dir(),
            "models",
            "fixtures",
            "dbt_1_9",
            "simple_model.yml",
        )
        data = load_yaml(path)
        dbt_schema = LightdashV20(**data)
        if dbt_schema.version:
            self.assertEqual(dbt_schema.version.value, 2)
        expected_model_name = "orders_model"

        # Assert non-null and use type casting for linter
        self.assertIsNotNone(dbt_schema.models)
        models = cast(list, dbt_schema.models)

        # Validate models list has expected length
        self.assertEqual(len(models), 1)
        self.assertGreater(len(models), 0)

        # Access first model
        first_model = models[0]
        self.assertEqual(first_model.name, expected_model_name)

        # Assert non-null for columns
        self.assertIsNotNone(first_model.columns)
        columns = cast(list, first_model.columns)

        # Validate columns list has expected elements
        self.assertGreaterEqual(len(columns), 2)

        # Test first column
        first_column = columns[0]
        self.assertEqual(first_column.name, "user_id")

        # Assert non-null for meta and metrics
        self.assertIsNotNone(first_column.meta)
        meta0 = first_column.meta
        self.assertIsNotNone(meta0.metrics)
        metrics0 = cast(dict, meta0.metrics)

        self.assertEqual(
            metrics0["distinct_user_ids"].type.value,
            "count_distinct",
        )

        # Test second column
        second_column = columns[1]
        self.assertEqual(second_column.name, "revenue")

        # Assert non-null for second column meta and metrics
        self.assertIsNotNone(second_column.meta)
        meta1 = second_column.meta
        self.assertIsNotNone(meta1.metrics)
        metrics1 = cast(dict, meta1.metrics)

        self.assertEqual(
            metrics1["sum_revenue"].type.value,
            "sum",
        )
