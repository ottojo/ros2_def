#!/usr/bin/env python3
import random
import rosbag2_py


def create_reader(uri: str, storage_identifier: str) -> (rosbag2_py.SequentialReader, rosbag2_py.ConverterOptions):
    reader = rosbag2_py.SequentialReader()
    storage_options = rosbag2_py.StorageOptions(uri, storage_id=storage_identifier)
    serialization_format = "cdr"
    converter_options = rosbag2_py.ConverterOptions(serialization_format, serialization_format)
    reader.open(storage_options, converter_options)
    return reader, converter_options


def create_writer(uri: str, converter_options: rosbag2_py.ConverterOptions, storage_identifier: str):
    writer = rosbag2_py.SequentialWriter()
    storage_options = rosbag2_py.StorageOptions(uri, storage_id=storage_identifier)
    writer.open(storage_options, converter_options)
    return writer


def main():
    bag_uri = "/home/gja38/aduulm_sandbox_sil/rosbag2_2023_05_12-13_11_59"
    prune_probability = 0.1

    metadata: rosbag2_py.BagMetadata = rosbag2_py.Info().read_metadata(bag_uri, "")
    reader, converter_options = create_reader(bag_uri, metadata.storage_identifier)
    writer = create_writer(bag_uri + "_converted", converter_options, metadata.storage_identifier)

    for topic_metadata in reader.get_all_topics_and_types():
        writer.create_topic(topic_metadata)

    while reader.has_next():
        topic_name, serialized_data, time_stamp_ns = reader.read_next()
        if random.random() > prune_probability:
            writer.write(topic_name, serialized_data, time_stamp_ns)


if __name__ == '__main__':
    main()
