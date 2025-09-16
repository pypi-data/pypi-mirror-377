# fmeflowclient
fmeflowclient is a simple Python 3.x library for communicating with an FME Flow server using its rest API.

## Install fmeflowclient
fmeflowclient is available on PyPI:

```bash
$ python -m pip install fmeflowclient
```

fmeflowclient is currently develop on Python 3.11.

## Sample usage
### Get all workspace owners
```python
from fmeflowclient import FMEFlowClient
fmecli = FMEFlowClient("https://fmeflow-fqdn/", token="FMETOKENHERE")

# Get a list of dictionaries of all workspaces
workspaces = fmecli.list_all_workspaces()

# Create a set of workspace owners
workspace_owners = {ws["userName"] for ws in workspaces}

print(workspace_owners)
```