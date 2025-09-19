"""
Video sources, that are the source from
where we will obtain the data to offer
as video in our editor.

These sources will be used by other
classes to access to the frames but 
improve the functionality and simplify
it.
"""
from yta_editor.utils import generate_silent_frames, get_videoframe_copy
from yta_editor.utils.alpha import update_transparency
from yta_editor.sources.abstract import _VideoSource
from yta_editor.utils.frame_generator import VideoFrameGenerator
from yta_video_pyav.reader import VideoReader
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from PIL import Image
from quicktions import Fraction
from typing import Union

import numpy as np


STATIC_VIDEO_DURATION = 99999.9
"""
A constant value to indicate for the
videos that are built with static
frames (frames that never change like
images or colors).
"""

class VideoFileSource(_VideoSource):
    """
    Class to represent a video, read from a
    video file, as a video media source.
    """

    @property
    def copy(
        self
    ) -> 'VideoFileSource':
        """
        Get a copy of this instance.
        """
        return VideoFileSource(self.filename)

    @property
    def ticks_per_frame(
        self
    ) -> int:
        """
        The number of ticks per video frame. A
        tick is the minimum amount of time and
        is the way 'pts' is measured, in ticks.

        This means that the 'pts' value will
        be increased this amount from one video
        frame to the next one.

        How we obtain it:
        - `(1 / fps) / time_base`
        """
        return self.reader.ticks_per_frame
    
    @property
    def duration(
        self
    ) -> Fraction:
        """
        The duration of the video.
        """
        return self.reader.duration
    
    @property
    def number_of_frames(
        self
    ) -> Union[int, None]:
        """
        The number of frames of the video.
        """
        return self.reader.number_of_frames
    
    @property
    def fps(
        self
    ) -> Union[Fraction, None]:
        """
        The frames per second of the video.
        """
        return self.reader.fps
    
    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The frames per second of the audio.
        """
        return self.reader.audio_fps

    @property
    def codec_name(
        self
    ) -> Union[str, None]:
        """
        The name of the codec.
        """
        return self.reader.codec_name
    
    @property
    def pixel_format(
        self
    ) -> Union[str, None]:
        """
        The pixel format.
        """
        return self.reader.pixel_format

    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video frames expressed 
        like (width, height).
        """
        return self.reader.size
    
    @property
    def width(
        self
    ) -> int:
        """
        The width of the video frames in pixels.
        """
        return self.size[0]
    
    @property
    def height(
        self
    ) -> int:
        """
        The height of the video frames in pixels.
        """
        return self.size[1]
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the video.
        """
        return self.reader.time_base
    
    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio.
        """
        return self.reader.audio_time_base

    def __init__(
        self,
        filename: str
    ):
        # TODO: Validate the 'filename' is actually
        # a valid and readable video file

        self.filename: str = filename
        """
        The filename of the original video.
        """
        # TODO: Detect the 'pixel_format' from the
        # extension (?)
        self.reader: VideoReader = VideoReader(self.filename)
        """
        The pyav video reader.
        """

    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment, using the video cache system, read
        from the file.
        """
        return self.reader.get_frame(t)
    
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction] = None
    ):
        """
        Get the audio frames for the given 't' time
        moment of the video using the audio frame
        cache.
        """
        return self.reader.get_audio_frames_at_t(t, video_fps)

class VideoImageSource(_VideoSource):
    """
    Class to represent a video, made from an
    image, as a video media source.

    This source is static. The same video
    frame will be returned always.
    """

    @property
    def copy(
        self
    ) -> 'VideoImageSource':
        """
        Get a copy of this instance.
        """
        return VideoImageSource(
            filename = self.filename,
            do_include_alpha = self._do_include_alpha,
            frame_format = self._frame_format,
            size = self._size,
            audio_fps = self.audio_fps,
            audio_samples_per_frame = self.audio_samples_per_frame
        )

    @property
    def duration(
        self
    ) -> float:
        """
        The duration of the source.
        """
        return STATIC_VIDEO_DURATION
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video frame, expressed as
        (width, height).
        """
        return (self.frame.width, self.frame.height)

    @property
    def frame(
        self
    ) -> VideoFrame:
        """
        The frame that must be displayed.
        """
        # By default we use it accepting transparency
        # TODO: The image must be like this:
        # arr = np.array(img)  # shape (h, w, 4), dtype=uint8
        # TODO: What value if no alpha (?)
        if not hasattr(self, '_frame'):
            self._frame = VideoFrame.from_ndarray(
                array = self._image,
                format = self._frame_format
            )
            
        return get_videoframe_copy(self._frame)

    def __init__(
        self,
        filename: str,
        do_include_alpha: bool = True,
        frame_format: str = 'rgba',
        size: Union[tuple[int, int], None] = None,
        audio_fps: int = 44_100,
        audio_samples_per_frame: int = 1024,
    ):
        """
        If the 'size' parameter is None, the image
        size will be used as the video size. If it
        is provided, the video frames will be 
        resized to fit the value provided.

        The 'audio_fps' and 'audio_samples_per_frame'
        are needed to generate the silent frames,
        and their values must match the ones in the
        general editor Timeline.
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)
        # TODO: Validate 'filename' is a valid
        # and readable image file

        self.filename: str = filename
        """
        The filename of the original image.
        """
        self._do_include_alpha: bool = do_include_alpha
        """
        The internal flag to indicate if we
        want to consider the alpha channel or
        not.
        """
        self._frame_format: str = frame_format
        """
        The frame format we want to apply.
        """
        self._size: Union[tuple[int, int], None] = size
        """
        The size of the video the user has
        requested when creating the video. Use
        the 'size' property to get the real 
        video size.
        """
        self.audio_fps: int = audio_fps
        """
        The fps (or sample rate) of the audio.
        """
        self.audio_samples_per_frame: int = audio_samples_per_frame
        """
        The amount of samples per audio frame.
        """

        self._image: np.ndarray = image_to_numpy_pillow(
            filename = filename,
            do_include_alpha = do_include_alpha,
            size = size
        )
        """
        The image that will be used to make the
        frame that will be played its whole
        duration.
        """

    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment.
        """
        # TODO: I keep this method to have the same
        # in all the clases, but it makes no sense
        # because it is the property itself and the
        # 't' parameter is ignored
        return self.frame
    
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction] = None
    ):
        """
        Get the audio frames for the given 't' time
        moment of the video using the audio frame
        cache.
        """
        silent_frames = generate_silent_frames(
            fps = video_fps,
            audio_fps = self.audio_fps,
            audio_samples_per_frame = self.audio_samples_per_frame,
            # TODO: Where do this 2 formats come from (?)
            #layout = self._track.audio_layout,
            #format = self._track.audio_format
        )

        for frame in silent_frames:
            yield frame._frame
    
class VideoColorSource(_VideoSource):
    """
    Class to represent a video, made from a
    static color, as a video media source.

    This source is static. The same video
    frame will be returned always.
    """

    @property
    def copy(
        self
    ) -> 'VideoColorSource':
        """
        Get a copy of this instance.
        """
        return VideoColorSource(
            color = self._color,
            size = self.size,
            frame_format = self._frame_format,
            transparency = self._transparency,
            audio_fps = self.audio_fps,
            audio_samples_per_frame = self.audio_samples_per_frame
        )

    @property
    def duration(
        self
    ) -> float:
        """
        The duration of the source.
        """
        return STATIC_VIDEO_DURATION
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video frame, expressed as
        (width, height), once it's been generated.
        """
        return (self.frame.width, self.frame.height)

    @property
    def frame(
        self
    ) -> VideoFrame:
        """
        The frame that must be displayed.
        """
        if not hasattr(self, '_frame'):
            # TODO: Use the 'color' parameter provided
            # in the '__init__' method
            self._frame = VideoFrameGenerator().background.full_white(
                size = self._size,
                transparency = self._transparency
            )

        # We return a copy to avoid modifying the
        # original once it's been sent
        return get_videoframe_copy(self._frame)

    def __init__(
        self,
        # TODO: Apply format to 'color'
        color: any,
        size: tuple[int, int] = (1920, 1080),
        frame_format: str = 'rgba',
        transparency: Union[float, None] = 1.0,
        audio_fps: int = 44_100,
        audio_samples_per_frame: int = 1024,
    ):
        """
        The 'transparency' must be a float between
        0.0 (opaque) and 1.0 (transparent).
        """
        # TODO: Apply format to 'color'
        self._color: any = color
        """
        The color that will be used to make the
        frame that will be played its whole
        duration.
        """
        self._size: tuple[int, int] = size
        """
        The size of the media frame requested by
        the user.
        """
        self._frame_format: str = frame_format
        """
        The frame format we want to apply.
        """

        # We need to check that the transparency
        # is according to the frame format
        transparency = update_transparency(
            transparency = transparency,
            format = frame_format
        )

        self._transparency: Union[float, None] = transparency
        """
        The transparency we want to apply if the
        frame format provided accepts transparency.
        """
        self.audio_fps: int = audio_fps
        """
        The fps (or sample rate) of the audio.
        """
        self.audio_samples_per_frame: int = audio_samples_per_frame
        """
        The amount of samples per audio frame.
        """

    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment.
        """
        # TODO: I keep this method to have the same
        # in all the clases, but it makes no sense
        # because it is the property itself and the
        # 't' parameter is ignored
        return self.frame
    
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction] = None
    ):
        """
        Get the audio frames for the given 't' time
        moment of the video using the audio frame
        cache.
        """
        silent_frames = generate_silent_frames(
            fps = video_fps,
            audio_fps = self.audio_fps,
            audio_samples_per_frame = self.audio_samples_per_frame,
            # TODO: Where do these 2 formats come from (?)
            #layout = self._track.audio_layout,
            #format = self._track.audio_format
        )

        for frame in silent_frames:
            yield frame._frame
    
class VideoNumpySource(_VideoSource):
    """
    Class to represent a video, made from a
    numpy array, as a video media source.

    This source is static. The same video
    frame will be returned always.
    """

    @property
    def copy(
        self
    ) -> 'VideoNumpySource':
        """
        Get a copy of this instance.
        """
        return VideoNumpySource(
            array = self._array,
            fps = self.fps,
            duration = self.duration
        )

    @property
    def duration(
        self
    ) -> float:
        """
        The duration of the source.
        """
        return STATIC_VIDEO_DURATION
    
    @property
    def size(
        self
    ) -> tuple[int, int]:
        """
        The size of the video frame, expressed as
        (width, height).
        """
        return (self.frame.width, self.frame.height)

    # TODO: Put some information about the
    # shape we need to pass, and also create
    # a 'size' property with the size of the
    # array
    @property
    def frame(
        self
    ) -> VideoFrame:
        """
        The frame that must be displayed.
        """
        # By default we use it accepting transparency
        # TODO: The image must be like this:
        # arr = np.array(img)  # shape (h, w, 4), dtype=uint8
        # TODO: What value if no alpha (?)
        return VideoFrame.from_ndarray(
            array = self._array,
            format = 'rgba'
        )

    def __init__(
        self,
        array: np.ndarray,
        fps: Union[int, float, Fraction] = 60,
        duration: Union[int, float, Fraction] = 1,
        audio_fps: int = 44_100,
        audio_samples_per_frame: int = 1024,
    ):
        self._array: np.ndarray = array
        """
        The array of information that will be
        used to make the frame that will be
        played its whole duration.
        """
        self.fps: Fraction = Fraction(fps)
        """
        The frames per second of this video source.
        """
        self.duration: Fraction = Fraction(duration)
        """
        The duration of this video source.
        """
        self.audio_fps: int = audio_fps
        """
        The fps (or sample rate) of the audio.
        """
        self.audio_samples_per_frame: int = audio_samples_per_frame
        """
        The amount of samples per audio frame.
        """

    def get_video_frame_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment.
        """
        # TODO: I keep this method to have the same
        # in all the clases, but it makes no sense
        # because it is the property itself and the
        # 't' parameter is ignored
        return self.frame
    
    def get_audio_frames_at_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction] = None
    ):
        """
        Get the audio frames for the given 't' time
        moment of the video using the audio frame
        cache.
        """
        silent_frames = generate_silent_frames(
            fps = video_fps,
            audio_fps = self.audio_fps,
            audio_samples_per_frame = self.audio_samples_per_frame,
            # TODO: Where do this 2 formats come from (?)
            #layout = self._track.audio_layout,
            #format = self._track.audio_format
        )

        for frame in silent_frames:
            yield frame._frame

    



# TODO: I think I have this util in another
# library, so please check it...
def image_to_numpy_pillow(
    filename: str,
    do_include_alpha: bool = True,
    size: Union[tuple[int, int], None] = None
) -> 'np.ndarray':
    """
    Read the imagen file 'filename' and transform
    it into a numpy, reading also the alpha channel.

    If the 'size' parameter is None, the original
    size will be preserved. If no, it will be resized
    using the pillow LANCZOS resize method.
    """
    mode = (
        'RGBA'
        if do_include_alpha else
        'RGB'
    )

    image = Image.open(filename)
    image = (
        image.resize(size, Image.LANCZOS)
        if size is not None else
        image
    )
    image = image.convert(mode)

    return np.array(image)

"""
The pyav uses Pillow to load an image as
a numpy array but using not the alpha.
"""