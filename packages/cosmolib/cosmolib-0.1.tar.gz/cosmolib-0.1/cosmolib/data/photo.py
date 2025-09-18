from __future__ import annotations
import numpy as np
from dataclasses import dataclass

TYPE_CHECKING = False
if TYPE_CHECKING:
    from os import PathLike
    from typing import Any, TypeAlias
    from numpy.typing import NDArray

    _DictKey: TypeAlias = str | int | tuple["_DictKey", ...]


def normalize_result_axis(
    axis: tuple[int, ...] | int | None,
    result: NDArray[Any],
    ell: tuple[NDArray[Any], ...] | NDArray[Any] | None,
) -> tuple[int, ...]:
    """
    Normalize the axis argument for result arrays.

    Returns a tuple of axis indices, handling None and negative values.
    """
    try:
        from numpy.lib.array_utils import normalize_axis_tuple
    except ModuleNotFoundError:
        from numpy.lib.stride_tricks import normalize_axis_tuple  # type: ignore

    if axis is None:
        if result.ndim == 0:
            axis = ()
        elif isinstance(ell, tuple):
            axis = tuple(range(-len(ell), 0))
        else:
            axis = -1
    return normalize_axis_tuple(axis, result.ndim, "axis")

@dataclass(frozen=True, repr=False)
class AngularPowerSpectrum:
    """
    Result: A sleek dataclass for LSS numerical results and metadata.
    for angular power spectra and mixing matrix results.

    Attributes:
        array: Main result data (always float dtype).
        ell: Optional ellipsoid or error data.
        axis: Axis or axes for the result.
        lower: Optional lower bounds.
        upper: Optional upper bounds.
        weight: Optional weights.
        software: Optional software identifier.
    """

    array: NDArray[Any]
    ell: NDArray[Any] | tuple[NDArray[Any], ...] | None = None
    axis: int | tuple[int, ...] | None = None
    lower: NDArray[Any] | tuple[NDArray[Any], ...] | None = None
    upper: NDArray[Any] | tuple[NDArray[Any], ...] | None = None
    weight: NDArray[Any] | tuple[NDArray[Any], ...] | None = None
    software: str | None = None

    def __post_init__(self) -> None:
        # Ensure array is float dtype for consistency
        float_array = np.asarray(self.array, dtype=float)
        object.__setattr__(self, "array", float_array)

        # Normalize axis after setting array
        axis = normalize_result_axis(self.axis, self.array, self.ell)
        object.__setattr__(self, "axis", axis)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(axis={self.axis!r})"


    def __array__(
    self,
    dtype: np.dtype[Any] | None = None,
    *,
    copy: bool | None = None,
    ) -> NDArray[Any]:
        """
        Allow Result to be used as a NumPy array.
        """
        if copy is not None:
            return self.array.__array__(dtype, copy=copy)
        return self.array.__array__(dtype)

    def __getitem__(self, key: Any) -> Any:
        """
        Index into the result array.
        """
        return self.array[key]

    @property
    def ndim(self) -> int:
        """Number of dimensions."""
        return self.array.ndim

    @property
    def shape(self) -> tuple[int, ...]:
        """Shape of the result array."""
        return self.array.shape

    @property
    def dtype(self) -> np.dtype[Any]:
        """Data type of the result array."""
        return self.array.dtype
