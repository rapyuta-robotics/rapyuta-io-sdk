Configuration module 
======================================

As a robotic developer, you need to represent, store, and review parameters. Additionally, you might want to access parameters in your source code, modify a subset of parameters for a particular robot, or add new parameters and apply those to a group of robots.

The rapyuta.io platform provides a mechanism that allows a developer to set, review, update and override configuration for any connected robot. Configuration parameters in the rapyuta.io platform are represented by a tree-like hierarchical structure called configuration hierarchy.



.. toctree::
   :maxdepth: 3
   :caption: Contents:
   

Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, upload_configurations, download_configurations, apply_parameters
