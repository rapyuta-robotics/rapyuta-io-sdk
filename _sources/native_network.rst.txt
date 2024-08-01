Native Network module
======================================


rapyuta.io provides a way to establish robot to robot communication without using brokered solution in a local network. The main purpose of native network is to give the same communication mechanism as present in a single shared ROS master.



.. toctree::
   :maxdepth: 3
   :caption: Contents:


Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, list_native_networks, get_native_network, create_native_network, delete_native_network



Native Network Module
------------------------

.. automodule:: rapyuta_io.clients.native_network
    :members:
    :exclude-members: get_deserialize_map,get_serialize_map

.. autoclass:: rapyuta_io.clients.common_models.InternalDeploymentStatus
    :members:
    :exclude-members: get_deserialize_map,get_serialize_map
