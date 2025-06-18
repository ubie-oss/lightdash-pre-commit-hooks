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

import abc
from typing import List, Union

from lightdash_pre_commit.parsers.lightdash_dbt_2_0 import LightdashV20
from lightdash_pre_commit.parsers.lightdash_dbt_2_5 import LightdashV25


# ruff: noqa: B024
class BaseChecker(abc.ABC):
    """Base class for all checkers."""

    @classmethod
    def check(cls, data: Union[LightdashV20, LightdashV25], **kwargs) -> List[str]:
        """Check the data and return a list of errors."""
        raise NotImplementedError
