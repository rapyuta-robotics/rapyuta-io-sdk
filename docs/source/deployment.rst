Deployment module 
======================================


A deployment is a rapyuta.io resource that represents a unique instantiation of a rapyuta.io package. It holds information about the package deployed, the configuration used, and interfaces exposed. It possesses a unique identifier and provides a mechanism to introspect its phase and state that are needed to ascertain the state of a system.

Tooling such as logs, debug terminals and other automation leverage this uniquely identifiable resource to allow the operator to manage, debug and observe a particular running instance of their application.

Deployments support composition patterns to allow the user to combine multiple different applications to help realize a potentially more complex robotics solution.


.. toctree::
   :maxdepth: 3
   :caption: Contents:


Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, get_deployment, get_all_deployments, update_deployment



Deployments Module
------------------------

.. automodule:: rapyuta_io.clients.deployment
    :members: