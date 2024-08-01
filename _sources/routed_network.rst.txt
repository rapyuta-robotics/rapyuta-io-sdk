Routed Network module 
======================================


rapyuta.io implements various features for automatically linking different deployments, and hence, aid software composition. It implements a dedicated communication plane for ROS.

Routed network is a rapyuta.io resource to enable ROS communication between different ROS package deployments.
Binding a routed network resource to your deployment will enable other deployments on the same routed network to consume ROS topics/services/actions as defined in the package. 
Data flow occurs only when another package chooses to subscribe to a topic, call a service or call an action.


.. toctree::
   :maxdepth: 3
   :caption: Contents:
   

Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, get_all_routed_networks, get_routed_network, create_cloud_routed_network, create_device_routed_network, delete_routed_network



Routed Network Module
------------------------

.. automodule:: rapyuta_io.clients.routed_network
    :members:

.. autoclass:: rapyuta_io.clients.common_models.InternalDeploymentStatus
    :members:
    :exclude-members: get_deserialize_map,get_serialize_map