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
"""py.test configuration."""

import os
from pathlib import Path

import nibabel as nb
import numpy as np
import pytest

test_data_env = os.getenv("TEST_DATA_HOME", str(Path.home() / "nifreeze-tests"))
test_output_dir = os.getenv("TEST_OUTPUT_DIR")
test_workdir = os.getenv("TEST_WORK_DIR")

_datadir = (Path(__file__).parent.parent.parent / "test" / "data").absolute()


def pytest_report_header(config):
    return f"""\
TEST_DATA_HOME={test_data_env}.
TEST_OUTPUT_DIR={test_output_dir or "<unset> (output files will be discarded)"}.
TEST_WORK_DIR={test_workdir or "<unset> (intermediate files will be discarded)"}.
"""


@pytest.fixture(autouse=True)
def doctest_imports(doctest_namespace):
    """Populates doctests with some conveniency imports."""
    doctest_namespace["np"] = np
    doctest_namespace["nb"] = nb
    doctest_namespace["os"] = os
    doctest_namespace["Path"] = Path
    doctest_namespace["repodata"] = _datadir
