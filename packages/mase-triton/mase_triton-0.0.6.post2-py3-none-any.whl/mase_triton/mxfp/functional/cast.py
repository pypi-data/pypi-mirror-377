import torch
from torch import Tensor

from ...utils.meta import device_str, dtype_str, shape_tuple
from .. import fake as mxfp_fake
from .. import kernels as mxfp_kernels
from ..helpers import flatten_for_quantize, permute_for_dequantize
from ..meta import MXFPMeta, MXFPTensorMeta


def extract_mxfp_components(
    tensor: Tensor, block_dim: int, mxfp_meta: MXFPMeta
) -> tuple[Tensor, Tensor, MXFPTensorMeta]:
    """
    Extracts the MXFP components from a tensor.

    .. note::
        The block for exponent sharing is a 1D vector instead of a 2D matrix.

    :param tensor: The input tensor to be quantized.
    :type tensor: torch.Tensor
    :param block_dim: The dimension to group the tensor elements into blocks.
    :type block_dim: int
    :param mxfp_meta: The metadata for the MXFP format.
    :type mxfp_meta: MXFPMeta

    :returns: The extracted scales, elements, and tensor metadata.
    :rtype: tuple[torch.Tensor, torch.Tensor, MXFPTensorMeta]
    """
    device = device_str(tensor.device)
    ori_shape = shape_tuple(tensor.shape)
    ori_dtype = dtype_str(tensor.dtype)
    ndim = len(ori_shape)
    assert block_dim < ndim and block_dim >= -ndim

    tensor = flatten_for_quantize(tensor, block_dim)
    if device.startswith("cuda"):
        scales, elements = mxfp_kernels.extract_mxfp_components(
            tensor, mxfp_meta=mxfp_meta
        )
    else:
        scales, elements = mxfp_fake.extract_mxfp_components(
            tensor, mxfp_meta=mxfp_meta
        )

    tensor_meta = MXFPTensorMeta(
        device=device,
        dtype=ori_dtype,
        shape=ori_shape,
        block_dim=block_dim,
        meta=mxfp_meta,
    )
    return scales, elements, tensor_meta


def compose_mxfp_tensor(
    scales,
    elements,
    tensor_meta: MXFPTensorMeta,
    output_dtype: torch.dtype | None = None,
) -> Tensor:
    """
    Compose a tensor from MXFP components.

    :param scales: The shared scales for exponent sharing.
    :type scales: torch.Tensor
    :param elements: The elements of the tensor.
    :type elements: torch.Tensor
    :param tensor_meta: The metadata for the MXFP tensor.
    :type tensor_meta: MXFPTensorMeta
    :param output_dtype: The desired data type of the output tensor, by default None, which uses the dtype from tensor_meta.
    :type dtype: torch.dtype, optional

    :returns: The dequantized tensor.
    :rtype: torch.Tensor
    """
    device = tensor_meta.device
    output_dtype = (
        getattr(torch, tensor_meta.dtype) if output_dtype is None else output_dtype
    )

    if device.startswith("cuda"):
        tensor = mxfp_kernels.compose_mxfp_tensor(
            scales=scales,
            elements=elements,
            mxfp_meta=tensor_meta.meta,
            output_dtype=output_dtype,
        )
    else:
        tensor = mxfp_fake.compose_mxfp_tensor(
            scales=scales,
            elements=elements,
            mxfp_meta=tensor_meta.meta,
            output_dtype=output_dtype,
        )

    tensor = permute_for_dequantize(
        tensor, ori_shape=tensor_meta.shape, block_dim=tensor_meta.block_dim
    )
    return tensor


def quantize_dequantize(
    tensor: Tensor,
    block_dim: int,
    mxfp_meta: MXFPMeta,
    output_dtype: torch.dtype | None = None,
) -> Tensor:
    """
    Quantizes and dequantizes a tensor using the MXFP format.

    :param tensor: The input tensor to be quantized.
    :type tensor: torch.Tensor
    :param block_dim: The dimension to group the tensor elements into blocks.
    :type block_dim: int
    :param mxfp_meta: The metadata for the MXFP format.
    :type mxfp_meta: MXFPMeta
    :param output_dtype: The desired data type of the output tensor, by default None, which uses the dtype from mxfp_meta.

    :returns: The dequantized tensor.
    :rtype: torch.Tensor
    """
    scales, elements, tensor_meta = extract_mxfp_components(
        tensor, block_dim, mxfp_meta
    )
    tensor_dq = compose_mxfp_tensor(
        scales, elements, tensor_meta, output_dtype=output_dtype
    )
    return tensor_dq
