# -*- coding: utf-8 -*-

import abc
import os
from typing import cast
from uuid import uuid4

from sinapsis_core.data_containers.data_packet import AudioPacket, DataContainer
from sinapsis_core.template_base.base_models import OutputTypes, TemplateAttributes, UIPropertiesMetadata

from sinapsis_data_readers.helpers.tags import Tags
from sinapsis_data_readers.templates.base_file_data_loader import _BaseDataReader


class _AudioBaseReader(_BaseDataReader):
    PACKET_ATT_NAME = "audios"
    UIProperties = UIPropertiesMetadata(
        output_type=OutputTypes.AUDIO,
        tags=[Tags.AUDIO, Tags.READERS],
    )

    class AttributesBaseModel(TemplateAttributes):
        """
        Attributes for the AudioBaseReader.

        audio_file_path (str):
            Path to the audio file to be read.

        source (str):
            The source identifier, defaults to "streamlit".
        """


        root_dir: str | None = None
        audio_file_path: str
        source: str = str(uuid4())

    @abc.abstractmethod
    def read_file(self) -> AudioPacket | None:
        """Abstract method to read the audio data.

        This method must be implemented by subclasses to
        read the audio data and return an AudioPacket with the content
        of the audio.

        Returns:
            AudioPacket: The audio data wrapped in an AudioPacket.
        """
    def get_full_path(self):
        audio_file_path = cast(str, self.attributes.audio_file_path)
        full_path = os.path.join(self.attributes.root_dir, audio_file_path)
        return full_path

    def has_elements(self) -> bool:
        """Flag to indicate if there is still content to process"""
        return True

    def append_packets_to_container(self, container: DataContainer) -> None:
        """Adds a packet to the input container

        Args:
            container (DataContainer): container where data is to be appended
        """
        data_packets_to_add = [self.read_file()]
        if data_packets_to_add:
            data_packets_to_add += getattr(container, self.PACKET_ATT_NAME)
        setattr(container, self.PACKET_ATT_NAME, data_packets_to_add)

    def make_data_entries(self) -> list[AudioPacket]:
        audio_packets: list[AudioPacket] = []
        return audio_packets
