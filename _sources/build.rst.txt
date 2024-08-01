Build modules
======================================


Builds on rapyuta.io are a fundamental resource which convert your source code residing in your VCS into a container image.

Builds can be referenced when creating packages and enables an end-to-end “Code to Deployment” pipeline for your Robotics solution.



.. toctree::
   :maxdepth: 3
   :caption: Contents:
   

Client Module
-----------------


.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, list_builds, create_build, get_build, delete_build, trigger_build, rollback_build


Build
-----------------

.. automodule:: rapyuta_io.clients.build
    :members:
    :exclude-members: is_ready, poll_till_ready

Operations on Builds
---------------------

.. automodule:: rapyuta_io.clients.buildoperation
    :members: