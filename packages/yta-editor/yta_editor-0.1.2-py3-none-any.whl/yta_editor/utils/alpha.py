from typing import Union

import numpy as np


def numpy_videoframe_has_alpha_pixels(
    frame: 'np.ndarray'
) -> bool:
    """
    Check if the provided numpy array has alpha
    pixels or not. If the provided numpy array
    doesn't include an alpha layer the result
    will be False.
    """
    return (
        frame.ndim == 3 and
        frame.shape[2] > 3 and
        np.any(frame[..., 3] < 255)
    )

def videoframe_has_alpha_layer(
    frame: 'VideoFrame'
) -> bool:
    """
    Check if the provided 'frame' pyav VideoFrame
    has alpha layer or not, that is defined by an
    'a' in the frame format name. This doesn't 
    mean that some pixel is transparent, it only
    means that there is an alpha layer, but the
    frame could be completely opaque.

    The code:
    - `'a' in frame.format.name`
    """
    return 'a' in frame.format.name

def update_transparency(
    transparency: Union[float, None],
    format: Union[str, None] = None
) -> Union[float, None]:
    """
    Update the provided 'transparency' value,
    that must be a value in the [0.0, 1.0] range,
    if necessary.

    If the 'format' is provided:
    - Alpha format will force an opaque alpha
    transparency if it is None
    - Non-alpha format will force a None value
    if transparency is provided
    """
    return (
        # Alpha format, no transparency => opaque
        0.0
        if (
            transparency is None and
            format is not None and
            'a' in format 
        ) else
        # Non-alpha format but transparency => None
        None
        if (
            transparency is not None and
            format is not None and
            'a' not in format
        ) else
        # Lower than 0.0 limit
        0.0
        if (
            transparency is not None and
            transparency < 0.0
        ) else
        # Greater than 1.0 limit
        1.0
        if (
            transparency is not None and
            transparency > 1.0
        ) else
        transparency
    )