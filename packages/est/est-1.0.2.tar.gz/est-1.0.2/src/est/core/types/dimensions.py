from typing import Optional
from typing import Sequence

import numpy
from numpy.typing import ArrayLike

DimensionsType = Sequence[int]
# Dimensions of X, Y and Channel/Energy.

STANDARD_DIMENSIONS = (2, 1, 0)
# The standard dataset axes are (Channel/Energy, Y, X).


def validate_dimensions_type(dimensions: DimensionsType) -> None:
    if len(dimensions) != 3:
        raise TypeError("Dimensions should have three integers")
    if set(dimensions) != {0, 1, 2}:
        raise TypeError("Dimensions should have three values: 0, 1 and 2")


def parse_dimensions(dimensions: Optional[DimensionsType]) -> DimensionsType:
    if dimensions is None:
        return STANDARD_DIMENSIONS
    validate_dimensions_type(dimensions)
    return dimensions


def transform_to_standard(data: ArrayLike, dimensions: DimensionsType) -> ArrayLike:
    dimensions = parse_dimensions(dimensions)
    src_axis = (0, 1, 2)
    dst_axis = (
        dimensions.index(STANDARD_DIMENSIONS[0]),
        dimensions.index(STANDARD_DIMENSIONS[1]),
        dimensions.index(STANDARD_DIMENSIONS[2]),
    )
    if src_axis == dst_axis:
        return data
    return numpy.moveaxis(data, src_axis, dst_axis)
