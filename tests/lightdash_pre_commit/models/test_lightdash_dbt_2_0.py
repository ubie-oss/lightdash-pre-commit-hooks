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

from lightdash_pre_commit.models.lightdash_dbt_2_0 import LightdashV20
from tests.lightdash_pre_commit.utils import get_test_root_dir, load_yaml


class TestLightdashV20(unittest.TestCase):
    """Test the LightdashV20 model."""

    def test_parse_simple_model_schema(self):
        path = os.path.join(
            get_test_root_dir(),
            "models",
            "fixtures",
            "lightdash_dbt_2_0",
            "simple_model.yml",
        )
        data = load_yaml(path)
        dbt_schema = LightdashV20(**data)
        self.assertIsNotNone(dbt_schema.version)
        self.assertEqual(dbt_schema.version.value, 2)
        expected_model_name = "orders_model"
        self.assertEqual(
            dbt_schema.models[0].name, expected_model_name
        )  # pylint: disable=unsubscriptable-object
        self.assertEqual(
            dbt_schema.models[0].columns[0].name, "user_id"
        )  # pylint: disable=unsubscriptable-object
        self.assertEqual(
            dbt_schema.models[0]  # pylint: disable=unsubscriptable-object
            .columns[0]
            .meta.metrics["distinct_user_ids"]
            .type.value,
            "count_distinct",
        )
        self.assertEqual(
            dbt_schema.models[0].columns[1].name, "revenue"
        )  # pylint: disable=unsubscriptable-object
        self.assertEqual(
            dbt_schema.models[0]
            .columns[1]
            .meta.metrics["sum_revenue"]
            .type.value,  # pylint: disable=unsubscriptable-object
            "sum",
        )
