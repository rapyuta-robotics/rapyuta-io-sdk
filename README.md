# Rapyuta.io Python SDK

Rapyuta.io Python SDK enables you to access platform services and resources in
your python applications.

The SDK supports Python 3.8+. For older Python 2.x support, you can use the
0.x.x [releases](https://pypi.org/project/rapyuta-io/#history) from Pypi.

## Install

The SDK is distributed through PyPi index, and can be installed directly using `pip`.

```bash
pip install rapyuta-io
```

To install the SDK from source, you can use the `setup.py` script directly.
Clone the repository and from the root of the directory, run the following
command.

``` bash
python setup.py install
```

## Getting Started

Before using the SDK, you need the Rapyuta Token. You can get it from
[here](https://auth.rapyuta.io/authToken/).

``` python
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
```

