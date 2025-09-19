from yta_editor.utils.frame_generator import AudioFrameGenerator
from yta_editor.utils.frame_wrapper import AudioFrameWrapped
from yta_video_frame_time.t_fraction import fps_to_time_base
from yta_video_opengl.effects import EffectsStack
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from quicktions import Fraction
from typing import Union


def audio_frames_and_remainder_per_video_frame(
    # TODO: Maybe force 'fps' as int (?)
    video_fps: Union[float, Fraction],
    sample_rate: int, # audio_fps
    number_of_samples_per_audio_frame: int
) -> tuple[int, int]:
    """
    Get how many full silent audio frames we
    need and the remainder for the last one
    (that could be not complete), according
    to the parameters provided.

    This method returns a tuple containing
    the number of full silent audio frames
    we need and the number of samples we need
    in the last non-full audio frame.
    """
    # Video frame duration (in seconds)
    time_base = fps_to_time_base(video_fps)
    sample_rate = Fraction(int(sample_rate), 1)

    # Example:
    # 44_100 / 60 = 735  ->  This means that we
    # will have 735 samples of sound per each
    # video frame
    # The amount of samples per frame is actually
    # the amount of samples we need, because we
    # are generating it...
    samples_per_frame = sample_rate * time_base
    # The 'nb_samples' is the amount of samples
    # we are including on each audio frame
    full_audio_frames_needed = samples_per_frame // number_of_samples_per_audio_frame
    remainder = samples_per_frame % number_of_samples_per_audio_frame
    
    return int(full_audio_frames_needed), int(remainder)

"""
These methods below are shared by the
Audio and Video class that handle and
wrap an audio or video.
"""
def apply_video_effects_to_frame_at_t(
    effects_stack: EffectsStack,
    frame: VideoFrame,
    t: Union[int, float, 'Fraction']
) -> Union[VideoFrame, 'ndarray']:
    """
    Apply the video effects to the given
    'frame' on the 't' time moment provided.

    This method should be called before 
    yielding any frame.
    """
    ParameterValidator.validate_mandatory_instance_of('frame', frame, VideoFrame)
    ParameterValidator.validate_mandatory_instance_of('effects_stack', effects_stack, EffectsStack)

    if len(effects_stack.video_effects) == 0:
        return frame

    # TODO: I think this has to preserve the
    # transparency if any of the video frames
    # that are passed to this method (from 
    # the different layers) have an alpha
    # channel or we will lose it in the
    # process... By now I'm just forcing the
    # format that comes. Or maybe not,
    # because when a frame comes and has no
    # transparency, the next frames will be
    # not visible (if coming ordered by
    # priority)... Well... maybe I'm confused
    # right now and this just modifies a 
    # single frame or a frame that has been
    # combined previously, so no worries...

    # We handle frames as 'rgb24' or 'rgba' and
    # then reformat to the expected format (if
    # needed)
    temp_format = (
        'rgba'
        if (
            frame.format != 'rgba' and
            'a' in frame.format
        ) else
        'rgb24'
        if (
            frame.format != 'rgb24' and
            'a' not in frame.format
        ) else
        frame.format
    )

    # Need the frame as a numpy
    new_frame = frame.to_ndarray(format = temp_format)

    new_frame = effects_stack.apply_video_effects_at_t(
        frame = new_frame,
        # The 't' here is the internal valid one
        t = t
    )

    # Rebuild the VideoFrame
    new_frame = VideoFrame.from_ndarray(
        array = new_frame,
        format = temp_format
    )

    new_frame = (
        new_frame.reformat(format = frame.format)
        if frame.format != temp_format else
        new_frame
    )

    # We don't actually need these data
    # because we will overwrite it when
    # processing the combined output
    new_frame.time_base = (
        frame.time_base
        if frame.time_base is not None else
        Fraction(1, 60)
    )
    new_frame.pts = (
        frame.pts
        if frame.pts is not None else
        0
    )

    return new_frame

def apply_audio_effects_to_frame_at_t(
    effects_stack: EffectsStack,
    frame: Union['AudioFrame', 'ndarray'],
    t: Union[int, float, 'Fraction']
) -> Union['AudioFrame', 'ndarray']:
    """
    Apply the audio effects to the given
    'frame' on the 't' time moment provided.

    This method should be called before 
    yielding any frame.
    """
    # TODO: I think we shouldn't receive a
    # 'ndarray' here, it must be AudioFrame
    ParameterValidator.validate_mandatory_instance_of('frame', frame, [AudioFrame, 'ndarray'])

    # Need the frame as a numpy
    new_frame = (
        frame.to_ndarray()
        if PythonValidator.is_instance_of(frame, AudioFrame) else
        frame
    )
    
    new_frame = effects_stack.apply_audio_effects_at_t(
        frame = new_frame,
        # The 't' here is the internal valid one
        t = t
    )

    # Rebuild the AudioFrame
    new_frame = AudioFrame.from_ndarray(
        array = new_frame,
        format = frame.format,
        layout = frame.layout
    )
    new_frame.sample_rate = frame.sample_rate
    # We don't actually need these data
    # because we will overwrite it when
    # processing the combined output
    new_frame.time_base = (
        frame.time_base
        if frame.time_base is not None else
        Fraction(1, 60)
    )
    new_frame.pts = (
        frame.pts
        if frame.pts is not None else
        0
    )

    return new_frame


# TODO: Is this method here ok (?)
def generate_silent_frames(
    fps: int,
    audio_fps: int,
    audio_samples_per_frame: int,
    layout: str = 'stereo',
    format: str = 'fltp'
) -> list[AudioFrameWrapped]:
    """
    Get the audio silent frames we need for
    a video with the given 'fps', 'audio_fps'
    and 'audio_samples_per_frame', using the
    also provided 'layout' and 'format' for
    the audio frames.

    This method is used when we have empty
    parts on our tracks and we need to 
    provide the frames, that are passed as
    AudioFrameWrapped instances and tagged as
    coming from empty parts.
    """
    audio_frame_generator: AudioFrameGenerator = AudioFrameGenerator()

    # Check how many full and partial silent
    # audio frames we need
    number_of_frames, number_of_remaining_samples = audio_frames_and_remainder_per_video_frame(
        video_fps = fps,
        sample_rate = audio_fps,
        number_of_samples_per_audio_frame = audio_samples_per_frame
    )

    # The complete silent frames we need
    silent_frame = audio_frame_generator.silent(
        sample_rate = audio_fps,
        layout = layout,
        number_of_samples = audio_samples_per_frame,
        format = format,
        pts = None,
        time_base = None
    )
    
    frames = (
        [
            AudioFrameWrapped(
                frame = silent_frame,
                is_from_empty_part = True
            )
        ] * number_of_frames
        if number_of_frames > 0 else
        []
    )

    # The remaining partial silent frames we need
    if number_of_remaining_samples > 0:
        silent_frame = audio_frame_generator.silent(
            sample_rate = audio_fps,
            # TODO: Check where do we get this value from
            layout = layout,
            number_of_samples = number_of_remaining_samples,
            # TODO: Check where do we get this value from
            format = format,
            pts = None,
            time_base = None
        )
        
        frames.append(
            AudioFrameWrapped(
                frame = silent_frame,
                is_from_empty_part = True
            )
        )

    return frames

def get_videoframe_copy(
    video_frame: VideoFrame
) -> 'VideoFrame':
    """
    Create a copy of the provided VideoFrame
    instance. This is similar to .copy().
    """
    return VideoFrame.from_ndarray(
        array = video_frame.to_ndarray(format = video_frame.format.name),
        format = video_frame.format.name
    )