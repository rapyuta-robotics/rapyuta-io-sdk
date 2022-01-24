Organization module
======================================


Organization is the representation of a group of users on the Platform. Every user must be part of at least one organization.

Each Organization has:

- Auto-generated unique organization ID.
- An organization name, which you provide.
- miscellaneous metadata: e.g., creator name, timestamp, etc.
- You may add multiple users to the same organization.



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
    :members: __init__

Organization Module
-----------------

.. automodule:: rapyuta_io.clients.organization
    :members:
    :exclude-members: get_deserialize_map,get_serialize_map

