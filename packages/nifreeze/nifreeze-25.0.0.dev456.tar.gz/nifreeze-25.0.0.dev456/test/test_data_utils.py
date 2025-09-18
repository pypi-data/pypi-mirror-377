import nibabel as nb
import numpy as np
import numpy.testing as npt

from nifreeze.data.utils import apply_affines


def test_apply_affines(request):
    rng = request.node.rng

    # Create synthetic dataset
    nii_data = rng.random((10, 10, 10, 10))

    # Generate Nifti1Image
    nii = nb.Nifti1Image(nii_data, np.eye(4))

    # Generate synthetic affines
    em_affines = np.expand_dims(np.eye(4), 0).repeat(nii_data.shape[-1], 0)

    nii_t = apply_affines(nii, em_affines)

    npt.assert_allclose(nii.dataobj, nii_t.dataobj)
    npt.assert_array_equal(nii.affine, nii_t.affine)
