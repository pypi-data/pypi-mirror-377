# -*- coding: utf-8 -*-


import os

import numpy as np
from sinapsis_core.data_containers.annotations import ImageAnnotations
from sinapsis_core.data_containers.data_packet import ImagePacket
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR

from sinapsis_data_readers.helpers.csv_reader import read_file
from sinapsis_data_readers.helpers.tags import Tags
from sinapsis_data_readers.templates.base_file_data_loader import (
    ContentNotSetException,
    _BaseDataReader,
)


class CSVImageDataset(_BaseDataReader):
    """
    A dataset reader for CSV-based image datasets, inheriting from _BaseDataReader.

    This class loads image data from a CSV file, processes the data into ImagePackets,
    and provides methods for reading the image data and handling the image processing.

    Usage example:

        agent:
          name: my_test_agent
        templates:
        - template_name: InputTemplate
          class_name: InputTemplate
          attributes: {}
        - template_name: CSVImageDataset
          class_name: CSVImageDataset
          template_input: InputTemplate
          attributes:
            data_dir: '/path/to/data/dir'
            pattern: '**/*'
            batch_size: 1
            shuffle_data: false
            samples_to_load: -1
            load_on_init: false
            height: 28
            width: 28


    """

    PACKET_ATT_NAME = "images"
    UIProperties = UIPropertiesMetadata(
        category="CSV", output_type=OutputTypes.IMAGE, tags=[Tags.CSV, Tags.IMAGE, Tags.DATASET, Tags.READERS]
    )

    class AttributesBaseModel(_BaseDataReader.AttributesBaseModel):  # type:ignore
        """Attributes for the CSV Image template.

        Attributes:
            height (int): The height of each image.
            width (int): The width of each image.
        """

        height: int = 28
        width: int = 28

    def __init__(self, attributes: TemplateAttributeType) -> None:
        """
        Initializes the CSVImageDataset instance by reading the CSV data and setting up attributes.

        Args:
            attributes (dict): A dictionary containing dataset configuration and attributes.
        """
        # Ensure 'data_dir' is available and convert it to string if it's not None
        data_dir = getattr(self.attributes, "data_dir", None)
        root_dir = getattr(self.attributes, "root_dir", SINAPSIS_CACHE_DIR)
        if data_dir is None:
            raise ValueError("The 'data_dir' attribute cannot be None.")
        full_path = os.path.join(root_dir, data_dir)
        self.data_points = read_file(full_path)
        super().__init__(attributes)

    def read_packet_content(self, packet: ImagePacket) -> None:
        """
        Reads and processes the content of a given ImagePacket by reshaping the image data.

        Args:
            packet (ImagePacket): The ImagePacket to be processed.

        Raises:
            ContentNotSetException: If the content of the packet is not properly set.
        """
        image = np.array(packet.content, dtype="uint8")
        image = image.reshape(self.attributes.height, self.attributes.width)
        packet.content = image

    def make_data_entries(self) -> list[ImagePacket]:
        """
        Creates a list of ImagePackets from the loaded CSV data points.

        Each data entry consists of an image (with label and pixel data),
        and is encapsulated in an ImagePacket object.

        Returns:
            list[ImagePacket]: A list of ImagePacket objects representing the dataset.

        Notes:
            If the `load_on_init` attribute is set to True, the image data is processed immediately
            using `read_packet_content`. If any packet cannot be processed (due to missing or invalid content),
            it is skipped.
        """
        image_packets: list[ImagePacket] = []
        # Iterate through the data points (only up to the specified number of samples)
        for idx, data_point in enumerate(self.data_points.values[: self.attributes.samples_to_load]):
            label = data_point[0]  # The first column is the label
            value = data_point[1:,]  # Remaining columns are the image data

            # Create an ImagePacket for this data point
            image_packet = ImagePacket(
                source=f"{self.attributes.data_dir}_{idx}",
                content=value,
                color_space=self.attributes.color_space,
                annotations=[ImageAnnotations(label=label, label_str=str(label))],
                id=label,
            )

            if self.attributes.load_on_init:
                try:
                    self.read_packet_content(image_packet)
                except ContentNotSetException:
                    continue

            image_packets.append(image_packet)

        return image_packets
