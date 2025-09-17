# Copyright 2025 - Pruna AI GmbH. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pruna.algorithms.pruna_base import PrunaAlgorithmBase
from pruna.config.smash_space import COMPILER
from pruna.engine.save import SAVE_FUNCTIONS


class PrunaCompiler(PrunaAlgorithmBase):
    """Base class for compilation algorithms."""

    algorithm_group = COMPILER
    # compiled models can not be saved most of the time
    # we have to save the model before compiling and reapply the compilation when loading
    save_fn = SAVE_FUNCTIONS.save_before_apply
