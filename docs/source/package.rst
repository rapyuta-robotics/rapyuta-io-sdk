Package module
======================================


A package is a fundamental rapyuta.io resource that represents a declaration of your application. It is the smallest unit of deployment in rapyuta.io, and it can be deployed either on a device or the cloud or both.

To make this possible a package must encapsulate any information about how it should be built, its compatibility and runtime requirements, network endpoints and ROS interfaces it exposes, and any configuration information it may require.




.. toctree::
   :maxdepth: 3
   :caption: Contents:
   

Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, get_package, get_all_packages, 
              create_package, create_package_from_manifest, delete_package



Package Module
------------------------

.. automodule:: rapyuta_io.clients.package
    :members:

.. autoclass:: rapyuta_io.clients.plan.Plan
    :members:
    :exclude-members: get_component_id, get_component_by_name, needs_aliases, validate
