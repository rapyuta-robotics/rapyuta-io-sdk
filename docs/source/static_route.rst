Static Route module 
======================================


rapyuta.io enables you to create a static route URL and give it a globally unique FQDN. When you add a static route, an externally exposed endpoint is essentially guaranteed to be available at the URL of that particular static route. It makes externally exposed endpoints (and hence the deployments exposing them) resilient to failure or re-deployment, facilitates maintenance and upgrades to the backend/deployment while retaining the same unique globally available URL.

Static routes are used frequently to get a deterministic URL/route for your application while exposing the network endpoint externally

.. toctree::
   :maxdepth: 3
   :caption: Contents:
   

Client Module
-----------------

.. autoclass:: rapyuta_io.rio_client.Client
    :members: __init__, get_all_static_routes, get_static_route, get_static_route_by_name, create_static_route, delete_static_route



Static Route Module
-------------------

.. automodule:: rapyuta_io.clients.static_route
    :members: