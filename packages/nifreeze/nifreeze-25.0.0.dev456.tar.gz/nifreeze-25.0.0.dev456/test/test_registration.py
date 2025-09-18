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
"""Unit tests exercising the estimator."""

from importlib.resources import files
from os import cpu_count

import nibabel as nb
import nitransforms as nt
import numpy as np
import pytest
from nibabel.affines import from_matvec
from nibabel.eulerangles import euler2mat
from nipype.interfaces.ants.registration import Registration

from nifreeze.registration.ants import _massage_mask_path
from nifreeze.registration.utils import displacements_within_mask


@pytest.mark.parametrize("r_x", [0.0, 0.1, 0.3])
@pytest.mark.parametrize("r_y", [0.0, 0.1, 0.3])
@pytest.mark.parametrize("r_z", [0.0, 0.1, 0.3])
@pytest.mark.parametrize("t_x", [0.0, 1.0])
@pytest.mark.parametrize("t_y", [0.0, 1.0])
@pytest.mark.parametrize("t_z", [0.0, 1.0])
@pytest.mark.parametrize("dataset", ["hcph", "dwi"])
# @pytest.mark.parametrize("dataset", ["dwi"])
def test_ANTs_config_b0(datadir, tmp_path, dataset, r_x, r_y, r_z, t_x, t_y, t_z):
    """Check that the registration parameters for b=0
    gives a good estimate of known affine"""

    fixed = datadir / f"{dataset}-b0_desc-avg.nii.gz"
    fixed_mask = datadir / f"{dataset}-b0_desc-brain.nii.gz"
    moving = tmp_path / "moving.nii.gz"

    b0nii = nb.load(fixed)
    T = from_matvec(euler2mat(x=r_x, y=r_y, z=r_z), (t_x, t_y, t_z))
    xfm = nt.linear.Affine(T, reference=b0nii)

    (~xfm).apply(b0nii, reference=b0nii).to_filename(moving)

    registration = Registration(
        terminal_output="file",
        from_file=files("nifreeze.registration").joinpath("config/b0-to-b0_level0.json"),
        fixed_image=str(fixed.absolute()),
        moving_image=str(moving.absolute()),
        fixed_image_masks=[str(fixed_mask)],
        random_seed=1234,
        num_threads=cpu_count(),
    )

    result = registration.run(cwd=str(tmp_path)).outputs
    xform = nt.linear.Affine(
        nt.io.itk.ITKLinearTransform.from_filename(result.forward_transforms[0]).to_ras(),
        reference=b0nii,
    )

    masknii = nb.load(fixed_mask)
    assert displacements_within_mask(masknii, xform, xfm).mean() < (
        0.6 * np.mean(b0nii.header.get_zooms()[:3])
    )


def test_massage_mask_path():
    """Test the case where a warning must be issued."""
    with pytest.warns(UserWarning, match="More mask paths than levels"):
        maskpath = _massage_mask_path(["/some/path"] * 2, 1)

    assert maskpath == ["/some/path"]
