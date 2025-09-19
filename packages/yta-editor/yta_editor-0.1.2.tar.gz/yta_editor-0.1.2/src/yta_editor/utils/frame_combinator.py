"""
TODO: I don't like the name nor the
location of this file, but it is here
to encapsulate some functionality 
related to combining video frames.

Module to contain methods that combine
video frames. Call them with the 2
frames you want to combine and you 
will get the combined frame as return.
"""
from av.audio.resampler import AudioResampler
from av.audio.frame import AudioFrame

import numpy as np


class VideoFrameCombinator:
    """
    Class to wrap the functionality related
    to combine different video frames.
    """

    @staticmethod
    def blend_alpha(
        bottom: np.ndarray,
        top: np.ndarray,
        alpha = 0.5
    ):
        return (alpha * top + (1 - alpha) * bottom).astype(np.uint8)

    @staticmethod
    def blend_add(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        Lighten the combined image, as if you
        were superimposing two light projectors.
        """
        return np.clip(bottom.astype(np.int16) + top.astype(np.int16), 0, 255).astype(np.uint8)

    @staticmethod
    def blend_multiply(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        It darkens, like projecting two
        transparencies together.
        """
        return ((bottom.astype(np.float32) * top.astype(np.float32)) / 255).astype(np.uint8)

    @staticmethod
    def blend_screen(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        It does the opposite of Multiply, it
        clarifies the image.
        """
        return (255 - ((255 - bottom.astype(np.float32)) * (255 - top.astype(np.float32)) / 255)).astype(np.uint8)

    @staticmethod
    def blend_overlay(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        Mix between Multiply and Screen
        depending on the brightness of each
        pixel.
        """
        b = bottom.astype(np.float32) / 255
        t = top.astype(np.float32) / 255
        mask = b < 0.5
        result = np.zeros_like(b)
        result[mask] = 2 * b[mask] * t[mask]
        result[~mask] = 1 - 2 * (1 - b[~mask]) * (1 - t[~mask])

        return (result * 255).astype(np.uint8)

    @staticmethod
    def blend_difference(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        Highlight the differences between the
        two frames.
        """
        return np.abs(bottom.astype(np.int16) - top.astype(np.int16)).astype(np.uint8)

    # TODO: This one needs a mask, thats why
    # it is commented
    # @staticmethod
    # def blend_mask(
    #     bottom,
    #     top,
    #     mask
    # ):
    #     """
    #     En lugar de un alpha fijo, puedes pasar una máscara (por ejemplo, un degradado o un canal alfa real)

    #     mask: array float32 entre 0 y 1, mismo tamaño que frame.
    #     """
    #     return (mask * top + (1 - mask) * bottom).astype(np.uint8)

class AudioFrameCombinator:
    """
    Class to wrap the functionality related
    to combine different audio frames.
    """

    @staticmethod
    def sum_tracks_frames(
        tracks_frames: list[AudioFrame],
        sample_rate: int = 44100,
        layout: str = 'stereo',
        format: str = 'fltp',
        do_normalize: bool = True
    ) -> AudioFrame:
        """
        Sum all the audio frames from the different
        tracks that are given in the 'tracks_frames'
        list (each column is a single audio frame of
        a track). This must be a list that should 
        come from a converted matrix that was
        representing each track in a row and the
        different audio frames for that track on each
        column.

        This method is to sum audio frames of one
        specific 't' time moment of a video.

        The output will be the sum of all the audio
        frames and it will be normalized to avoid
        distortion if 'do_normalize' is True (it is
        recommended).
        """
        if len(tracks_frames) == 0:
            raise Exception('The "tracks_frames" list of audio frames is empty.')
        
        arrays = []
        resampler: AudioResampler = AudioResampler(
            format = format,
            layout = layout,
            rate = sample_rate
        )

        for track_frame in tracks_frames:
            # Resample to output format
            # TODO: What if the resampler creates more
            # than one single frame? I don't know what
            # to do... I'll see when it happens
            print(track_frame)
            track_frame = resampler.resample(track_frame)
            
            if len(track_frame) > 1:
                print('[ ! ]   The resampler has given more than 1 frame...')

            track_frame_array = track_frame[0].to_ndarray()

            # Transform to 'float32' [-1, 1]
            # TODO: I think this is because the output
            # is 'fltp' but we have more combinations
            # so this must be refactored
            if track_frame_array.dtype == np.int16:
                track_frame_array = track_frame_array.astype(np.float32) / 32768.0
            elif track_frame_array.dtype != np.float32:
                track_frame_array = track_frame_array.astype(np.float32)

            # Mono to stereo if needed
            # TODO: What if source is 'stereo' and we
            # want mono (?)
            if (
                track_frame_array.shape[0] == 1 and
                layout == 'stereo'
            ):
                track_frame_array = np.repeat(track_frame_array, 2, axis = 0)

            arrays.append(track_frame_array)

        # Same length and fill with zeros if needed
        max_len = max(a.shape[1] for a in arrays)
        stacked = []
        for a in arrays:
            # TODO: Again, this 'float32' is because output
            # is 'fltp' I think...
            buf = np.zeros((a.shape[0], max_len), dtype = np.float32)
            buf[:, :a.shape[1]] = a
            stacked.append(buf)

        """
        All this below is interesting to avoid
        distortion or things like that, but it
        is actually making the volume decrease
        in these parts we combine the frames,
        so we are facing a higher volume in the
        segments in which we have one single
        audio and different volumes when more
        than one are being played together...

        Thats why I have this code commented by
        now.
        """
        if False:
            # We attenuate the audios
            # attenuation_gain = 1.0 / math.sqrt(len(arrays))
            # arrays = [
            #     arr * attenuation_gain
            #     for arr in arrays
            # ]

            # Sum all the sounds
            mix = np.sum(stacked, axis = 0)

            # if do_normalize:
            #     # Avoid distortion and saturation
            #     mix /= len(stacked)

            # # Avoid clipping
            # mix = np.clip(mix, -1.0, 1.0)
        else:
            mix = np.sum(stacked, axis = 0)

        out = AudioFrame.from_ndarray(
            array = mix,
            format = format,
            layout = layout
        )
        out.sample_rate = sample_rate

        return out

# TODO: This below is what I'm using to
# mix frames with alpha layer within the
# project, but should be put inside a
# class. By now its here to recognize it
# easier
def combine_videoframes_with_alpha_layer(
    top_frame: np.ndarray,
    bottom_frame: np.ndarray
) -> np.ndarray:
    """
    Combine 2 RGBA frames, that must be (h, w, 4)
    and uint8, with alpha blending. Useful to
    combine video frames with alpha blending.

    This method returns the new combined frame.
    """
    # To float in [0, 1] range
    top_frame_rgb = top_frame[..., :3].astype(np.float32) / 255.0
    bottom_frame_rgb = bottom_frame[..., :3].astype(np.float32) / 255.0
    top_frame_alpha = top_frame[..., 3:].astype(np.float32) / 255.0
    bottom_frame_alpha = bottom_frame[..., 3:].astype(np.float32) / 255.0

    # Alpha blending
    output_alpha = top_frame_alpha + bottom_frame_alpha * (1 - top_frame_alpha)
    # Avoid division by zero
    output_rgb = (top_frame_rgb * top_frame_alpha + bottom_frame_rgb * bottom_frame_alpha * (1 - top_frame_alpha)) / np.clip(output_alpha, 1e-6, 1.0)

    # Back to uint8
    output_frame = np.zeros_like(top_frame, dtype = np.uint8)
    output_frame[..., :3] = (output_rgb * 255).astype(np.uint8)
    output_frame[..., 3:] = (output_alpha * 255).astype(np.uint8)

    return output_frame
