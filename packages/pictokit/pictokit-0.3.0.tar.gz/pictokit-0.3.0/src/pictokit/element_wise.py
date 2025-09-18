import numpy as np
from beartype import beartype

from pictokit.constants import PIXEL_MAX, PIXEL_MIN


@beartype
def pixel_expansion(
    pixel: np.uint8 | int, low_limit: np.uint8 | int, high_limit: np.uint8 | int
) -> np.uint8:
    """
    Applies a contrast expansion transformation to a pixel by mapping values
    within a given range [low_limit, high_limit] to the full range [0, 255].

    If the `pixel` value falls within the specified interval, it is linearly
    rescaled to [0, 255]. Otherwise, the pixel value is returned unchanged.

    Args:
        pixel (int): Pixel value (0–255).
        low_limit (int): Lower bound of the intensity range (0–255).
        high_limit (int): Upper bound of the intensity range (0–255).

    Returns:
        int: The transformed pixel value in the range [0, 255].

    Raises:
        ValueError: If `pixel`, `low_limit`, or `high_limit` are outside the
            range [0, 255], or if `low_limit >= high_limit`.
    """
    args = {'pixel': pixel, 'low_limit': low_limit, 'high_limit': high_limit}
    for name, value in args.items():
        if not (PIXEL_MIN <= value <= PIXEL_MAX):
            raise ValueError(
                f'Expected {name} to be in the range 0 to 255, but received {value}'
            )
    if low_limit >= high_limit:
        raise ValueError(
            f'Lower limit must be strictly less than upper limit, '
            f'but received low_limit={low_limit}, high_limit={high_limit}'
        )
    if pixel > low_limit and pixel < high_limit:
        result = 255 / (high_limit - low_limit) * (pixel - low_limit)
    else:
        result = pixel

    result = np.uint8(result)
    return result


@beartype
def pixel_thresholding(
    pixel: int | np.uint8, T: int | np.uint8, A: int | np.uint8
) -> np.uint8:
    """Apply binary thresholding to a single pixel.

    This function implements the thresholding operation:

        f(D) = 0 if D > T else A*D

    Where:
        - D is the original pixel intensity.
        - T is the threshold value.
        - A is the intensity assigned to pixels above the threshold.

    All inputs must be within the 8-bit grayscale pixel range [0, 255].

    Args:
        pixel (int | np.uint8): Pixel intensity to evaluate.
        T (int | np.uint8): Threshold value.
        A (int | np.uint8): Intensity value assigned when pixel >= T.

    Returns:
        np.uint8: Thresholded pixel value (either 0 or A).

    Raises:
        ValueError: If `pixel`, `T`, or `A` are outside the range [0, 255].
    """
    for name, val in {'pixel': pixel, 'T': T, 'A': A}.items():
        if not (PIXEL_MIN <= int(val) <= PIXEL_MAX):
            raise ValueError(f'{name} must be in the range [0, 255], got {val}.')

    return np.uint8(A if pixel > T else pixel)


@beartype
def pixel_digital_negative(pixel: np.uint8 | int) -> np.uint8:
    """
    Compute the digital negative of a pixel.

    The digital negative is obtained by inverting the pixel intensity
    with respect to the maximum value (255), as follows:

        negative_pixel = 255 - pixel

    Args:
        pixel (np.uint8 | int): Original pixel value in the range [0, 255].

    Returns:
        np.uint8: Inverted pixel value (digital negative).

    Raises:
        ValueError: If the input value is outside the range [0, 255].
    """
    if not (PIXEL_MIN <= int(pixel) <= PIXEL_MAX):
        raise ValueError(f'pixel must be in the range [0, 255], got {pixel}.')

    return np.uint8(PIXEL_MAX - pixel)
