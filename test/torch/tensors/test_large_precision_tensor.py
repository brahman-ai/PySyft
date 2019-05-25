import numpy as np
import torch

from syft.frameworks.torch.tensors.interpreters import LargePrecisionTensor


def test_split_restore():
    bits = 32

    result_128 = LargePrecisionTensor._split_number(87721325272084551684339671875103718004, bits)
    result_64 = LargePrecisionTensor._split_number(4755382571665082714, bits)
    result_32 = LargePrecisionTensor._split_number(1107198784, bits)

    assert len(result_128) == 4
    assert len(result_64) == 2
    assert len(result_32) == 1

    assert (
        LargePrecisionTensor._restore_number(result_128, bits)
        == 87721325272084551684339671875103718004
    )
    assert LargePrecisionTensor._restore_number(result_64, bits) == 4755382571665082714
    assert LargePrecisionTensor._restore_number(result_32, bits) == 1107198784


def test_add():
    bits = 16
    expected = 9510765143330165428
    lpt1 = LargePrecisionTensor(np.array([4755382571665082714]), precision=bits)
    lpt2 = LargePrecisionTensor(np.array([4755382571665082714]), precision=bits)
    result = lpt1.add(lpt2)
    # The same number can be factorized in different ways. The sum of two matrices can be different to the
    # factorisation of the number the sum represents
    assert LargePrecisionTensor._restore_number(result.child.view(-1).tolist(), bits) == expected


def test_multiple_dimensions():
    bits = 16
    expected = torch.IntTensor([[[16894, 33600, 64302, 18778,  1357, 60759, 19791, 31352],
                                 [16894, 33600, 64302, 18778,  1357, 60759, 19791, 31352]],

                                [[16894, 33600, 64302, 18778,  1357, 60759, 19791, 31348],
                                 [16894, 33600, 64302, 18778,  1357, 60759, 19791, 31348]]])

    tensor = np.array([
        [87721325272084551684339671875103718008, 87721325272084551684339671875103718008],
        [87721325272084551684339671875103718004, 87721325272084551684339671875103718004]
    ])

    result = LargePrecisionTensor(tensor, precision=bits)

    assert torch.all(torch.eq(expected, result.child))


def test_multiple_dimensions_restore():
    bits = 16

    tensor = np.array([
        [87721325272084551684339671875103718008, 87721325272084551684339671875103718008],
        [87721325272084551684339671875103718004, 87721325272084551684339671875103718004]
    ])

    precision_tensor = LargePrecisionTensor(tensor, precision=bits)
    all_zeros = LargePrecisionTensor(np.zeros(tensor.shape))
    result = precision_tensor.add(all_zeros)
    assert result.shape == precision_tensor.shape


def test_dimensions_expanded():
    bits = 16

    tensor = np.array([
        [87721325272084551684339671875103718008, 87721325272084551684339671875103718008],
        [87721325272084551684339671875103718004, 87721325272084551684339671875103718004]
    ])

    precision_tensor = LargePrecisionTensor(tensor, precision=bits)
    all_zeros = LargePrecisionTensor(np.zeros(tensor.shape))

    all_zeros = all_zeros._adjust_to_shape(precision_tensor.shape)

    assert precision_tensor.shape == all_zeros.shape


def test_add_multiple_dimensions():
    bits = 16

    expected = 87721325272084551684339671875103719000
    tensor1 = LargePrecisionTensor(np.array([[87721325272084551684339671875103718008]]), precision=bits)
    tensor2 = LargePrecisionTensor(np.array([[992]]), precision=bits)

    result = tensor1.add(tensor2)
    assert LargePrecisionTensor._restore_number(result.child.view(-1).tolist(), bits) == expected
