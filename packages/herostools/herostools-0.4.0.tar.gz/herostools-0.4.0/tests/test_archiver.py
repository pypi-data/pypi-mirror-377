from jinja2 import Template
import time
from herostools.actor import ArrayArchiver, JsonArchiver
import numpy as np
import json


def test_array_archiver(local_hero_device, remote_hero_device, check_async_saved_np_file):
    metadata = {"path": "build/test", "filename": "test"}
    data_array = np.empty((2, 10))
    archiver = ArrayArchiver(
        object_selector="test_hero",
        event_name="np_event",
        default_metadata={"filename": "default_test"},
        save_template="{{ path }}/{{ filename }}.npy",
    )

    time.sleep(0.2)
    remote_hero_device.trigger_np(data_array, metadata)
    metadata.pop("filename")
    remote_hero_device.trigger_np(data_array, metadata)
    time.sleep(0.2)

    check_async_saved_np_file(f"{metadata['path']}/test.npy", data_array)
    check_async_saved_np_file(f"{metadata['path']}/default_test.npy", data_array)

    archiver.split_data_array = True
    archiver.name_template = Template("{{ path }}/{{ filename }}-{{ _split_index }}.npy")
    remote_hero_device.trigger_np(data_array, metadata)
    check_async_saved_np_file(f"{metadata['path']}/default_test-0.npy", data_array[0])


def test_json_archiver(local_hero_device, remote_hero_device):
    metadata = {"path": "build/test", "filename": "test"}
    data_dict = {"data": [0, 1, 2, 5, "test"]}
    archiver = JsonArchiver(
        object_selector="test_hero",
        event_name="json_event",
        default_metadata={"filename": "default_test"},
        save_template="{{ path }}/{{ filename }}.json",
    )

    remote_hero_device.trigger_json(data_dict, metadata)
    metadata.pop("filename")
    remote_hero_device.trigger_json(data_dict, metadata)
    time.sleep(0.2)

    with open(f"{metadata['path']}/test.json") as f:
        assert json.load(f) == data_dict

    with open(f"{metadata['path']}/default_test.json") as f:
        assert json.load(f) == data_dict

    archiver.merge_metadata = True
    remote_hero_device.trigger_json(data_dict, metadata)
    time.sleep(0.2)

    with open(f"{metadata['path']}/default_test.json") as f:
        assert json.load(f) == {
            "data": [0, 1, 2, 5, "test"],
            "metadata": {"filename": "default_test", "path": "build/test"},
        }
