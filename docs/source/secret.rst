Secret module
======================================

A secret is an object containing sensitive information or confidential data such as a password, SSH private key, SSL certificate.
It grants rapyuta.io access to private git repositories and private docker images so that the platform can build source code in private git repositories or use private docker images.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, create_secret,list_secrets,get_secret,delete_secret


Secret Module
-----------------
.. automodule:: rapyuta_io.clients.secret
    :members:
    :exclude-members: get_deserialize_map,get_serialize_map
