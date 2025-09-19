"""
The video frames must be built using the
(height, width) size when giving the numpy
array that will be used for it. We will
receive the values as (width, height) but
we will invert them when needed.

The frames that come from an empty part
are flagged with the .metadata attribute
'is_from_empty_part' so we can recognize
them and ignore when combining on the
timeline. We have that metadata in the
wrapper class we created.

TODO: Check because we have a similar
module in other project or projects.
"""
from yta_editor.utils.alpha import update_transparency
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.audio.layout import AudioLayout
from typing import Union

import numpy as np


class _FrameGenerator:
    """
    Class to generate frames as numpy arrays.
    """

    # TODO: I have some library doing this with
    # colors and numpy frames, so please refactor
    def full_black(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        transparency: Union[float, None] = None
    ) -> np.ndarray:
        """
        Get a numpy array that represents a full
        black frame of the given 'size' and with
        the given 'dtype'.

        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._get_numpy_array(
            color = (0, 0, 0),
            size = size,
            dtype = dtype,
            transparency = transparency
        )
    
    def full_white(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        transparency: Union[float, None] = None
    ) -> np.ndarray:
        """
        Get a numpy array that represents a full
        black frame of the given 'size' and with
        the given 'dtype'.

        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._get_numpy_array(
            color = (255, 255, 255),
            size = size,
            dtype = dtype,
            transparency = transparency
        )

    def full_red(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        transparency: Union[float, None] = None
    ) -> np.ndarray:
        """
        Get a numpy array that represents a full
        red frame of the given 'size' and with
        the given 'dtype'.
        
        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._get_numpy_array(
            color = (255, 0, 0),
            size = size,
            dtype = dtype,
            transparency = transparency
        )
    
    def full_green(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        transparency: Union[float, None] = None
    ) -> np.ndarray:
        """
        Get a numpy array that represents a full
        green frame of the given 'size' and with
        the given 'dtype'.
        
        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._get_numpy_array(
            color = (0, 255, 0),
            size = size,
            dtype = dtype,
            transparency = transparency
        )
    
    def full_blue(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        transparency: Union[float, None] = None
    ) -> np.ndarray:
        """
        Get a numpy array that represents a full
        blue frame of the given 'size' and with
        the given 'dtype'.
        
        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._get_numpy_array(
            color = (0, 0, 255),
            size = size,
            dtype = dtype,
            transparency = transparency
        )
    
    def _get_numpy_array(
        self,
        color: tuple[int, int, int],
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        transparency: Union[float, None] = None
    ) -> np.ndarray:
        """
        *For internal use only*

        Get the numpy array with the provided
        color and all the attributes set.

        The size must be (w, h).

        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        # Transparency in [0.0, 1.0] range
        transparency = update_transparency(transparency = transparency)

        """
        We handle transparency as a float value
        in the [0.0, 1.0] range, which is easy
        conceptually, but the RGBA frames are
        made different so we need to invert the
        values:
        - Full RGBA opaque value: 255
        - Full RGBA transparent value: 0
        """

        # Transparency to [0, 255] range where
        # 0 is transparent, 255 is opaque
        transparency = (
            int(round((1.0 - transparency) * 255))
            if transparency is not None else
            transparency
        )

        dimensions = (
            4
            if transparency is not None else
            3
        )

        fill_value = (
            color + (transparency,)
            if transparency is not None else
            color
        )

        return np.full(
            shape = (size[1], size[0], dimensions),
            fill_value = fill_value,
            dtype = dtype
        )

class _BackgroundFrameGenerator:
    """
    Internal class to simplify the way we
    access to the generation of background
    frames form the general generator class.
    """

    def __init__(
        self
    ):
        self._frame_generator: _FrameGenerator = _FrameGenerator()
        """
        Shortcut to the FrameGenerator.
        """

    def full_black(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        # TODO: I disable format by now because I
        # make it dynamic according to the 
        # 'transparency' value provided
        #format: str = 'rgb24',
        pts: Union[int, None] = None,
        time_base: Union['Fraction', None] = None,
        transparency: Union[float, None] = None
    ) -> VideoFrame:
        """
        Get a video frame that is completely black
        and of the given 'size'.

        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._full_color(
            color = 'black',
            size = size,
            dtype = dtype,
            pts = pts,
            time_base = time_base,
            transparency = transparency
        )
    
    def full_white(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        # TODO: I disable format by now because I
        # make it dynamic according to the 
        # 'transparency' value provided
        #format: str = 'rgb24',
        pts: Union[int, None] = None,
        time_base: Union['Fraction', None] = None,
        transparency: Union[float, None] = None
    ) -> VideoFrame:
        """
        Get a video frame that is completely white
        and of the given 'size'.

        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._full_color(
            color = 'white',
            size = size,
            dtype = dtype,
            pts = pts,
            time_base = time_base,
            transparency = transparency
        )

    def full_red(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        # TODO: I disable format by now because I
        # make it dynamic according to the 
        # 'transparency' value provided
        #format: str = 'rgb24',
        pts: Union[int, None] = None,
        time_base: Union['Fraction', None] = None,
        transparency: Union[float, None] = None
    ) -> VideoFrame:
        """
        Get a video frame that is completely red
        and of the given 'size'.

        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._full_color(
            color = 'red',
            size = size,
            dtype = dtype,
            pts = pts,
            time_base = time_base,
            transparency = transparency
        )
    
    # TODO: Refactor all this please
    def full_green(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        # TODO: I disable format by now because I
        # make it dynamic according to the 
        # 'transparency' value provided
        #format: str = 'rgb24',
        pts: Union[int, None] = None,
        time_base: Union['Fraction', None] = None,
        transparency: Union[float, None] = None
    ) -> VideoFrame:
        """
        Get a video frame that is completely green
        and of the given 'size'.

        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._full_color(
            color = 'green',
            size = size,
            dtype = dtype,
            pts = pts,
            time_base = time_base,
            transparency = transparency
        )

    def full_blue(
        self,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        # TODO: I disable format by now because I
        # make it dynamic according to the 
        # 'transparency' value provided
        #format: str = 'rgb24',
        pts: Union[int, None] = None,
        time_base: Union['Fraction', None] = None,
        transparency: Union[float, None] = None
    ) -> VideoFrame:
        """
        Get a video frame that is completely blue
        and of the given 'size'.

        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent) to be
        set, or None if you don't want transparency.

        Providing 'transparency' as None will 
        result in a numpy with only 3 dimensions.
        """
        return self._full_color(
            color = 'blue',
            size = size,
            dtype = dtype,
            pts = pts,
            time_base = time_base,
            transparency = transparency
        )
    
    def _full_color(
        self,
        color: str,
        size: tuple[int, int] = (1920, 1080),
        dtype: np.dtype = np.uint8,
        # TODO: I disable format by now because I
        # make it dynamic according to the 
        # 'transparency' value provided
        #format: str = 'rgb24',
        pts: Union[int, None] = None,
        time_base: Union['Fraction', None] = None,
        transparency: Union[float, None] = None
    ):
        """
        *For internal use only*

        Method that dynamically calls the internal
        method to generate the numpy according to
        the 'color' provided, that must fit the
        name of an existing method of the 
        '_FrameGenerator' instance.
        """
        format = (
            'rgba'
            if transparency is not None else
            'rgb24'
        )

        transparency = update_transparency(
            transparency = transparency,
            format = format
        )

        generator_method = getattr(self._frame_generator, f'full_{color}')

        frame = generator_method(
            size = size,
            dtype = dtype,
            transparency = transparency
        )

        return numpy_to_video_frame(
            frame = frame,
            format = format,
            pts = pts,
            time_base = time_base
        )

class VideoFrameGenerator:
    """
    Class to wrap the functionality related to
    generating a pyav video frame.

    This class is useful when we need to 
    generate the black background for empty
    parts within the tracks and in other 
    situations.
    """

    def __init__(
        self
    ):
        self.background = _BackgroundFrameGenerator()
        """
        Shortcut to the background creation.
        """

def numpy_to_video_frame(
    frame: np.ndarray,
    format: str = 'rgb24',
    pts: Union[int, None] = None,
    time_base: Union['Fraction', None] = None
) -> VideoFrame:
    """
    Transform the given numpy 'frame' into a
    pyav video frame with the given 'format'
    and also the 'pts' and/or 'time_base' if
    provided.
    """
    frame = VideoFrame.from_ndarray(
        # TODO: What if we want alpha (?)
        array = frame,
        format = format
    )

    if pts is not None:
        frame.pts = pts

    if time_base is not None:
        frame.time_base = time_base

    return frame

class AudioFrameGenerator:
    """
    Class to wrap the functionality related to
    generating a pyav audio frame.

    This class is useful when we need to 
    generate the silent audio for empty parts
    within the tracks and in other situations.
    """

    def silent(
        self,
        sample_rate: int,
        layout = 'stereo',
        number_of_samples: int = 1024,
        format = 's16',
        pts: Union[int, None] = None,
        time_base: Union['Fraction', None] = None
    ) -> AudioFrame:
        """
        Get an audio frame that is completely silent.
        This is useful when we want to fill the empty
        parts of our tracks.
        """
        dtype = audio_format_to_dtype(format)

        if dtype is None:
            raise Exception(f'The format "{format}" is not accepted.')

        # TODO: Is this raising exception if the
        # 'layout' is not valid? I think yes (?)
        number_of_channels = len(AudioLayout(layout).channels)

        # TODO: I leave these comments below because
        # I'm not sure what is true and what is not
        # so, until it is more clear... here it is:
        # For packed (or planar) formats we apply:
        # (1, samples * channels). This is the same
        # amount of data but planar, in 1D only
        # TODO: This wasn't in the previous version
        # and it was working, we were sending the
        # same 'number_of_samples' even when 'fltp'
        # that includes the 'p'
        # TODO: This is making the audio last 2x
        # if 'p' in format:
        #     number_of_samples *= number_of_channels

        silent_numpy_array = np.zeros(
            shape = (number_of_channels, number_of_samples),
            dtype = dtype
        )

        return numpy_to_audio_frame(
            frame = silent_numpy_array,
            sample_rate = sample_rate,
            layout = layout,
            format = format,
            pts = pts,
            time_base = time_base
        )
    
def numpy_to_audio_frame(
    frame: np.ndarray,
    sample_rate: int,
    layout: str = 'stereo',
    format: str = ' s16',
    pts: Union[int, None] = None,
    time_base: Union['Fraction', None] = None
) -> AudioFrame:
    """
    Transform the given numpy 'frame' into a
    pyav audio frame with the given 'sample_rate',
    'layout' and 'format, and also the 'pts
    and/or 'time_base' if provided.
    """
    frame = AudioFrame.from_ndarray(
        array = frame,
        format = format,
        layout = layout
    )

    frame.sample_rate = sample_rate

    if pts is not None:
        frame.pts = pts

    if time_base is not None:
        frame.time_base = time_base

    return frame

# TODO: Maybe transform into a Enum (?)
def audio_format_to_dtype(
    audio_format: str
) -> Union[np.dtype, None]:
    """
    Transform the given 'audio_format' into
    the corresponding numpy dtype value. If
    the 'audio_format' is not accepted this
    method will return None.

    This method must be used when we are
    building the numpy array that will be 
    used to build a pyav audio frame because
    the pyav 'audio_format' need a specific
    np.dtype to be built.

    For example, 's16' will return 'np.int16'
    and 'fltp' will return 'np.float32'.
    """
    return {
        's16': np.int16,
        'flt': np.float32,
        'fltp': np.float32
    }.get(audio_format, None)
    