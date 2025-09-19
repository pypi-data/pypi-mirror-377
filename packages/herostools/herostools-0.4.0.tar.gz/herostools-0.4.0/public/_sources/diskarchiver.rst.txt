===========================
HEROS Data Archiver
===========================

The HEROS data archiver subscribes to the :code:`new_data` event of a HERO and saves its payload to a file
path.

The filename for a given frame is then constructed using `Jinja2 <https://jinja.palletsprojects.com/en/stable/>`_
using the given meta data given as a dictionary. This allows to do math and postprocessing within the template.
For details on what can be implemented with templates, please refer to the official
`Jinja2 documentation <https://jinja.palletsprojects.com/en/stable/>`_.

Setup
-----
The data archiver can be started with BOSS as any other class using a json string as in the following example

.. code:: json


  {
    "_id": "my-camera-capturer",
    "classname": "herostools.actor.HERODataArchiver",
    "arguments": {
      "object_selector": "my-camera",
      "default_metadata": {
        "file_path": "/mnt/mystorage/images"
      },
      "save_template": "{{ file_path }}/testimg-{{ '%04d' % ( frame / 2 ) |round(0, 'floor') }}-{{ frame % 2 }}.npy"
    }
  }


The template generates file paths like the following

.. code:: bash

    /mnt/mystorage/images/testimg-0000-0.npy
    /mnt/mystorage/images/testimg-0000-1.npy
    /mnt/mystorage/images/testimg-0001-0.npy

assuming that :code:`frame` is a running iterator provided by the payload metadata. For example a camera abstracting from
:external+herosdevices:py:class:`herosdevices.core.templates.CameraTemplate` will generate such an event.
