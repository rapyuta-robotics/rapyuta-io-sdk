Device module 
======================================

A device is a rapyuta.io resource representing any physical device that typically lives at a client location and is registered on rapyuta.io. 
The resource encapsulates information about the device, its architecture, runtime, user-provided metadata.
Once a particular piece of hardware is successfully on-boarded to rapyuta.io this entity is responsible for providing the necessary mechanics and communication channels to manage and interact with the device. The platform leverages these mechanics to provide features that can be used to communicate to the device, configure it, monitor its health and deploy packages to the device.


.. toctree::
   :maxdepth: 1
   :caption: Contents:
   
Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, get_all_devices, get_device, create_device, delete_device, apply_parameters, toggle_features



Device Module
-----------------

.. automodule:: rapyuta_io.clients.device
    :members:

.. automodule:: rapyuta_io.clients.device_manager
    :members:

.. automodule:: rapyuta_io.clients.model
    :members:
    :exclude-members: get_deserialize_map,get_serialize_map
