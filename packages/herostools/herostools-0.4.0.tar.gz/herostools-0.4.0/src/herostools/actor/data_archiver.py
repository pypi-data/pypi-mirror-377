# coding:utf-8

from typing import Iterable
from abc import abstractmethod
from pathlib import Path
import json
import threading
import queue

import numpy as np
from jinja2 import Template

from heros import EventObserver

from heros.helper import log


from typing import Any


class HERODataArchiver(EventObserver):
    """
    This EventObserver subscribes to a user-definced event of a HERO and saves its payload to a file
    path. The event payload must have the form of an iterable with the first entry being the data and the second
    entry being a dictionary containing metadata.

    Args:
        object_selector: Zenoh object selector for the devices to subscribe to. In the simplest case this is the
            name of the target HERO
        event_name: Name of the event.
        default_metadata: A dictionary containing the default metadata.
        max_retries: In case storing the data failed, retry storing until :code:`max_retries`.

    Note:
        Do not use this class directly, use a child class which implements the method :meth:`_store`.
        For example, :class:`ArrayArchiver` assumes the data to be array-like and saves it as a numpy array.
    """

    def __init__(
        self,
        object_selector: str,
        event_name: str,
        default_metadata: dict | None = None,
        max_retries: int = 5,
        *args,
        **kwargs,
    ):
        self.metadata = default_metadata if default_metadata is not None else {}
        self.max_retries = int(max_retries)
        EventObserver.__init__(self, object_selector=object_selector, event_name=event_name, *args, **kwargs)

        # payload queue setup
        self._payload_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

        self.register_callback(self.feed)

    def _process_queue(self) -> None:
        """
        Background task to process the queue.
        """
        while not self._stop_event.is_set():
            try:
                source_name, payload, metadata, retry_count = self._payload_queue.get(timeout=1)
                log.debug(
                    f"Got data from queue source: {source_name}, metadata: {metadata}, retry_count: {retry_count}."
                )
                try:
                    self._store(source_name, payload, metadata)
                except Exception as e:
                    log.warning(f"Storing data from source: {source_name}, metadata: {metadata} failed with {e}.")
                    if retry_count < self.max_retries:
                        log.info(f"Re-queuing data from source: {source_name}, metadata: {metadata}.")
                        self.feed(source_name, (payload, metadata), retry_count + 1)
                    else:
                        log.error(
                            f"Max-retries exceeded for data from source: {source_name}, metadata: {metadata}. Dropping data!"
                        )
                finally:
                    self._payload_queue.task_done()
            except queue.Empty:
                continue

    def _stop(self):
        """
        Stop the background thread gracefully.
        """
        self._stop_event.set()
        self._worker_thread.join()

    def _teardown(self) -> None:
        """
        Teardown method is called by boss.
        """
        self._stop()

    def feed(self, source_name: str, data: Iterable, retry_count: int = 0) -> None:
        """
        Callback function called by the source event.

        Args:
            source_name: Name of the event source (the HERO).
            data: Data to be archived in the format (payload: object, metadata: dict)
            retry_count: Count how often this queue item was already encountered.
        """
        payload = data[0]
        metadata = self.metadata | data[1]
        log.debug(f"Feeding data from {source_name} with metadata {metadata}.")
        self._payload_queue.put((source_name, payload, metadata, retry_count))

    @abstractmethod
    def _store(self, source_name: str, payload: Any, metadata: dict) -> None:
        """
        Abstract method to store the payload.
        Must be implemented by subclasses.

        Args:
            source_name: Name of the event source (the HERO).
            payload: The actual data.
            metadata: The received metadata combined with the default metadata.
        """
        pass


class ArrayArchiver(HERODataArchiver):
    """
    This HERODataArchiver assumes the data to be numpy-like arrays and saves them as npy files.

    Args:
        object_selector: Zenoh object selector for the devices to subscribe to. In the simplest case this is the
            name of the target HERO
        event_name: Name of the event.
        save_template: The template from which the file name is generated.
            `Jinja2 <https://jinja.palletsprojects.com/en/stable/>`_ is used to generate a filename from the
            template using the given meta data given as a dictionary. Meta data can be supplied either by
            :code:`default_metadata` or obtained from the payload. For an example see the json example below.
        split_data_array: If True and the payload is an array, the observer will split the array into individual
            frames and save them as separate files. The key :code:`_split_index` can be used in :code:`save_template`
            to specify the subframe index in the filename.
        default_metadata: A dictionary containing the default metadata to be used when generating the filename.
        max_retries: In case storing the data failed, retry storing until :code:`max_retries`.

    Example:
        The class can be started with BOSS using a json string as in the following example::

            {
              "_id": "my-camera-capturer",
              "classname": "herostools.actor.ArrayArchiver",
              "arguments": {
                "object_selector": "my-camera",
                "event_name": "acquisition_data",
                "default_metadata": {
                  "file_path": "/mnt/mystorage/images"
                },
                "save_template": "{{ file_path }}/testimg-{{ '%04d' % ( frame / 2 ) |round(0, 'floor') }}-{{ frame % 2 }}.npy"
              }
            }

        The templates generates file paths like the following::

            /mnt/mystorage/images/testimg-0000-0.npy
            /mnt/mystorage/images/testimg-0000-1.npy
            /mnt/mystorage/images/testimg-0001-0.npy

        assuming that :code:`frame` is a running iterator provided by the payload metadata (i.e. a key in the metadata dictionary).
    """

    def __init__(
        self,
        save_template: str,
        split_data_array: bool = False,
        *args,
        **kwargs,
    ):
        self.name_template = Template(save_template)
        self.split_data_array = split_data_array
        HERODataArchiver.__init__(self, *args, **kwargs)

    def _store(self, source_name: str, payload: np.typing.NDArray[Any], metadata: dict) -> None:
        """
        Save data to a numpy array.
        The filename is generated from the jinja template using the metadata.

        Args:
            source_name: Name of the event source (the HERO).
            payload: The actual data as a numpy array.
            metadata: The received metadata combined with the default metadata.
        """
        metadata = self.metadata | metadata
        if self.split_data_array:
            for i_row, data_row in enumerate(payload):
                metadata["_split_index"] = i_row
                full_path = Path(self.name_template.render(metadata))
                full_path.parent.mkdir(parents=True, exist_ok=True)
                np.save(full_path, data_row)
        else:
            full_path = Path(self.name_template.render(metadata))
            full_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(self.name_template.render(metadata), payload)


class JsonArchiver(HERODataArchiver):
    """
    This HERODataArchiver assumes the data to be a dictionary and saves it as a json file.

    Args:
        object_selector: Zenoh object selector for the devices to subscribe to. In the simplest case this is the
            name of the target HERO
        event_name: Name of the event.
        save_template: The template from which the file name is generated.
            `Jinja2 <https://jinja.palletsprojects.com/en/stable/>`_ is used to generate a filename from the
            template using the given meta data given as a dictionary. Meta data can be supplied either by
            :code:`default_metadata` or obtained from the payload. For an example see the json example below.
        merge_metadata: If True,  merge the accompanying metadata to the data itself under the key :code:`metadata`..
        default_metadata: A dictionary containing the default metadata to be used when generating the filename.
    """

    def __init__(
        self,
        save_template: str,
        merge_metadata: bool = False,
        *args,
        **kwargs,
    ):
        self.name_template = Template(save_template)
        self.merge_metadata = merge_metadata
        HERODataArchiver.__init__(self, *args, **kwargs)

    def _store(self, source_name: str, payload: dict, metadata: dict) -> None:
        """
        Save data to a json file.
        The filename is generated from the jinja template using the metadata.

        Args:
            source_name: Name of the event source (the HERO).
            payload: The actual data.
            metadata: The received metadata combined with the default metadata.
        """

        metadata = self.metadata | metadata
        if self.merge_metadata:
            payload["metadata"] = metadata
        full_path = Path(self.name_template.render(metadata))
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(json.dumps(payload, indent=4))
