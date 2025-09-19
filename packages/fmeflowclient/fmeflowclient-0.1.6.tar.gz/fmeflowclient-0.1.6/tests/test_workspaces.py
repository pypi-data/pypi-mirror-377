import pytest

def test_live_workspaces(live_client):
    workspaces = live_client.workspaces.all()
    assert isinstance(workspaces, list)
    assert all('name' in ws for ws in workspaces)

    if workspaces and len(workspaces) > 0:
        first_workspace = workspaces[0]
        repo_name = first_workspace.get('repositoryName')
        ws_name = first_workspace.get('name')
        assert repo_name is not None
        assert ws_name is not None