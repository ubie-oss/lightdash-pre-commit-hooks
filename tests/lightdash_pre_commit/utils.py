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

import yaml  # type: ignore[import-untyped]


def get_test_root_dir() -> str:
    """
    Get the path to the test data directory.
    """
    return os.path.dirname(__file__)


def load_yaml(path: str) -> dict:
    """
    Load a YAML file and return its contents as a dictionary.
    """
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)
