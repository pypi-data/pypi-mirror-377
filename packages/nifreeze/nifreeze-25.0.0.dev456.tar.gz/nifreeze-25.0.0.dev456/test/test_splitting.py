# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
#
# Copyright The NiPreps Developers <nipreps@gmail.com>
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
#
# We support and encourage derived works from this project, please read
# about our expectations at
#
#     https://www.nipreps.org/community/licensing/
#
"""Unit test testing the lovo_split function."""

import numpy as np

from nifreeze.data.dmri import DWI
from nifreeze.data.splitting import lovo_split


def test_lovo_split(request, datadir):
    data = DWI.from_filename(datadir / "dwi.h5")

    # Set zeros in dataobj and gradients of the dwi object
    data.dataobj[:] = 0
    data.gradients[:] = 0

    # Select a random index
    rng = request.node.rng
    index = rng.integers(len(data))

    # Set 1 in dataobj and gradients of the dwi object at this specific index
    data.dataobj[..., index] = 1
    data.gradients[..., index] = 1

    # Apply the lovo_split function at the specified index
    train_data, test_data = lovo_split(data, index)

    # Check if the test data contains only 1s
    # and the train data contains only 0s after the split
    assert np.all(test_data[0] == 1)
    assert np.all(train_data[0] == 0)
    assert np.all(test_data[-1] == 1)
    assert np.all(train_data[-1] == 0)
