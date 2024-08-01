Persistent Volumes
======================================

Applications running on the cloud de-allocate any resources consumed when they stop, scale down, or fail. This implies that the working storage associated with them is ephemeral. To get around this problem rapyuta.io provides a mechanism to consume persistent block storage for your applications running in the cloud. This storage can be associated with at most one running deployment at any given point of time. A user is typically required to manage the lifecycle of the application code independently from the associated storage.

The Rapyuta IO Persistent Volume is a storage package. A storage package is a public package which is available to all users out of the box. You cannot delete or modify storage packages, and they are available to every user.

.. toctree::
   :maxdepth: 3
   :caption: Contents:
   

Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, get_persistent_volume, get_volume_instance




Persistent Volumes Module
---------------------------

.. automodule:: rapyuta_io.clients.persistent_volumes
    :members: