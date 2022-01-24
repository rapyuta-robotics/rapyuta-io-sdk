Project module
======================================


Any rapyuta.io resource that you create, or allocate and use must belong to a project. You can think of a project as the organizational unit for what you are building. A project is made up of the settings, configuration, and other metadata that describe your applications. Resources within a single project can work together easily, for example, by communicating through an internal network. The resources that each project contains remain separate across project boundaries; you can only interconnect them through an external connection.

Each project has:

- Auto-generated unique project ID
- A project name, which you provide.
- miscellaneous metadata: e.g., creator name, timestamp, etc.
- You may create multiple projects and use them to organize rapyuta.io resources.



.. toctree::
   :maxdepth: 3
   :caption: Contents:
   

.. autosummary::
   :toctree: _autosummary
   :template: custom-module-template.rst
   :recursive:

Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, list_projects, create_project,get_project, delete_project, set_project, add_user_to_project, remove_user_from_project

Project Module
-----------------

.. automodule:: rapyuta_io.clients.project
    :members:
    :exclude-members: get_deserialize_map,get_serialize_map

