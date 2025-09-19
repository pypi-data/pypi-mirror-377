"""
Methods for integrating the volume directly onto the exit plane.
"""

from abc import abstractmethod
from typing import Generic, TypeVar
from typing_extensions import override

import equinox as eqx
from equinox import AbstractClassVar
from jaxtyping import Array, Complex, Float

from ..._image_config import AbstractImageConfig
from ..._volume_parametrisation import AbstractVoxelVolume
from ..base_integrator import AbstractVolumeIntegrator, VolRepT


VoxelVolT = TypeVar("VoxelVolT", bound="AbstractVoxelVolume")


class AbstractDirectIntegrator(
    AbstractVolumeIntegrator[VolRepT], Generic[VolRepT], strict=True
):
    """Base class for a method of integrating a volume onto
    the exit plane.
    """

    is_projection_approximation: AbstractClassVar[bool]

    @abstractmethod
    @override
    def integrate(
        self,
        volume_representation: VolRepT,
        image_config: AbstractImageConfig,
        outputs_real_space: bool = False,
    ) -> (
        Complex[
            Array,
            "{image_config.padded_y_dim} {image_config.padded_x_dim//2+1}",
        ]
        | Complex[Array, "{image_config.padded_y_dim} {image_config.padded_x_dim}"]
        | Float[Array, "{image_config.padded_y_dim} {image_config.padded_x_dim}"]
    ):
        raise NotImplementedError


class AbstractDirectVoxelIntegrator(
    AbstractDirectIntegrator[VoxelVolT], Generic[VoxelVolT], strict=True
):
    outputs_integral: eqx.AbstractVar[bool]
