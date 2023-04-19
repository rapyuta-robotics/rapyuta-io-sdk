Welcome to Rapyuta.io SDK Documentation!
========================================

Rapyuta.io Python SDK enables you to access platform services and resources in
your python applications.

The SDK supports Python 3.6+. For older Python 2.x support, you can use the
0.x.x `releases <https://pypi.org/project/rapyuta-io/#history>`_ from Pypi.

Installation
------------

The SDK is distributed through PyPi index, and can be installed directly using
``pip``.

.. code:: bash    
    
    pip install rapyuta-io

To install the SDK from source, you can use the `setup.py` script directly.
Clone the repository and from the root of the directory, run the following
command.

.. code:: bash

    python setup.py install

Getting Started
---------------

Before using the SDK, you need the Rapyuta Token. You can get it from `here
<https://auth.rapyuta.io/authToken/>`_.

.. code-block:: python

    from rapyuta_io import Client

    TOKEN = "RAPYUTA_TOKEN"


    client = rapyuta_io.Client(TOKEN)

    # Create a Project and use it
    from rapyuta_io import Project

    project = client.create_project(Project("python-sdk"))
    client.set_project(project.guid)

    # Create a Build
    from rapyuta_io import Build, StrategyType, DeviceArch

    client.create_build(
        Build(
            "dummy",
            StrategyType.DOCKER,
            "https://github.com/ankitrgadiya/dummy-package",
            DeviceArch.AMD64,
        )
    )

You can read the documentation for individual resource modules:

.. toctree::
   :maxdepth: 1

   Authentication <auth>
   Organization <organization>
   Project <project>
   Secret  <secret>
   
   Device <device>

   Build <build>
   Package <package>
   Deployment <deployment>
   Parameters <parameter>
   Persistent Volumes <volumes>

   Routed Network <routed_network>
   Native Network <native_network>
   Static Route   <static_route>

   Rosbag <rosbag>
   Configuration <configuration>
   Metrics <metrics>

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
