# Copyright 2024 Adam McArthur
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

"""
Typehints specific to the hip_us package.
"""

from typing import Tuple

import numpy as np
from numpy.typing import NDArray

FemoralHeadSphere = Tuple[np.ndarray, np.ndarray, np.ndarray]
CoordinatesArray3D = NDArray[np.float64]
