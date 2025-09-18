# -*- coding: utf-8 -*-
import os.path

import torch
from sinapsis_core.data_containers.data_packet import ImagePacket
from torchcodec.decoders import SimpleVideoDecoder

from sinapsis_data_readers.helpers.tags import Tags
from sinapsis_data_readers.templates.video_readers.base_video_reader import (
    BaseVideoReader,
    NotSet,
    NotSetType,
    multi_video_wrapper,
)

VideoReaderTorchCodecUIProperties = BaseVideoReader.UIProperties
VideoReaderTorchCodecUIProperties.tags.extend([Tags.TORCHVIDEO])


class VideoReaderTorchCodec(BaseVideoReader):
    """Video reader template using TorchVideo's SimpleVideoDecoder.

    This class extends BaseVideoReader to implement video reading functionality
    using TorchVideo's SimpleVideoDecoder, enabling efficient loading and processing
    of video frames for deep learning applications.

    Usage example:
        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: VideoReaderTorchCodec
          class_name: VideoReaderTorchCodec
          template_input: InputTemplate
          attributes:
            video_file_path: '/path/to/video/file'
            batch_size: 1
            video_source: 4d2a355f-cda4-4742-9042-8e6ee842d1cf
            device: gpu
            loop_forever: false
    """

    UIProperties = VideoReaderTorchCodecUIProperties

    def make_video_reader(self) -> tuple[SimpleVideoDecoder, int] | NotSetType:
        """Initialize the video decoder and retrieve the total number of frames.

        This method attempts to create an instance of SimpleVideoDecoder with
        the specified video file path.

        Returns:
            tuple[SimpleVideoDecoder, int] | NotSet: A tuple containing the
            SimpleVideoDecoder instance and the total number of frames in the
            video. If the decoder cannot be created, it returns NotSet.

        Raises:
            ValueError: If there is an issue decoding the video file.
        """
        full_path = os.path.join(self.attributes.root_dir, self.attributes.video_file_path)
        try:
            video_reader = SimpleVideoDecoder(full_path)
        except ValueError as e:
            self.logger.warning(f"Was unable to decode video file: {e}")
            return NotSet
        return video_reader, video_reader.metadata.num_frames

    def close_video_reader(self) -> None:
        """Clean up resources associated with the video reader."""

    def _read_video_frames(self) -> list[ImagePacket]:
        """Read a batch of video frames from the SimpleVideoDecoder.

        This method retrieves a specified number of frames from the video decoder
        starting at the current frame count, processes them into ImagePacket objects,
        and returns them.

        Returns:
            list[ImagePacket]: A list of ImagePacket objects representing the
            video frames read from the decoder.
        """

        video_frames: list[ImagePacket] = []
        end_index = min(self.total_frames, self.frame_count + self.attributes.batch_size)
        torch_frames = self.video_reader[self.frame_count : end_index]
        for idx, frame in enumerate(torch_frames.data):
            video_frames.append(self._make_image_packet(frame, frame_index=self.frame_count + idx))
        return video_frames

    def reset_state(self, template_name: str | None = None) -> None:
        _ = template_name
        if self.attributes.device == "gpu":
            torch.cuda.empty_cache()
        super().reset_state(template_name)


@multi_video_wrapper
class MultiVideoReaderTorchCodec(VideoReaderTorchCodec):
    """Template to process multiple videos using Torch Codec
    The template extends the functionality of the VideoReaderTorchCodec template
    by adding as many video_readers as needed depending on the lenght of
    video_file_path list. It appends the dataframes of each of the videos to the
    ImagePacket object in DataContainer
    """
