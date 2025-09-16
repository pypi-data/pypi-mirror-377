import functools
import requests
from typing import List, Dict, Any
from typing import Optional

def _lazy_property(fn):
    """Decorator that makes a property lazy-evaluated."""
    # http://stevenloria.com/lazy-evaluated-properties-in-python/
    attr_name = "_lazy_" + fn.__name__

    @property
    @functools.wraps(fn)
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazy_property

class FMEFlowClient:
    '''
    FMEFlowClient provides a Python interface for interacting with the FME Flow REST API.
    This client allows you to authenticate with an FME Flow server, list repositories, retrieve all workspaces,
    run workspaces with parameters, and check the status of submitted jobs.
    '''
    def __init__(self, base_url: str, token: str, verify_ssl: bool = True) -> None:
        """
        Initializes the FME Flow client.

        Args:
            base_url (str): The base URL of the FME Flow server.
            token (str): The authentication token for FME Flow.
            verify_ssl (bool, optional): Whether to verify SSL certificates. Defaults to True.
        """
        self.base_url = base_url.rstrip('/') if base_url.endswith('/') else base_url
        self.api_url = base_url + '/fmerest/v3'
        self.headers = {
            'Authorization': f'fmetoken token={token}',
            'Accept': 'application/json'
        }
        self.verify_ssl = verify_ssl

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Sends an HTTP request to the FME Flow REST API.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint.
            **kwargs: Additional arguments to pass to the requests.request method.

        Returns:
            Any: The JSON-decoded response from the API.

        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        
        url = self.api_url + endpoint if endpoint.startswith('/') else self.api_url + '/' + endpoint
        url = url.rstrip('/')

        response = requests.request(
            method,
            url,
            headers=self.headers,
            verify=self.verify_ssl,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    
    def _http_get(self, endpoint: str, **kwargs) -> Any:
        return self._request("GET", endpoint, **kwargs)
    
    def _http_post(self, endpoint: str, **kwargs) -> Any:
        return self._request("POST", endpoint, **kwargs)
    
    @_lazy_property
    def automations(self) -> 'AutomationsManager':
        return AutomationsManager(self)
    
    @_lazy_property
    def licensing(self) -> 'LicensingManager':
        return LicensingManager(self)
    
    @_lazy_property
    def workspaces(self) -> 'WorkspaceManager':
        return WorkspaceManager(self)
    
    @_lazy_property
    def projects(self) -> 'ProjectManager':
        return ProjectManager(self)
    
    @_lazy_property
    def repositories(self) -> 'RepositoryManager':
        return RepositoryManager(self)
    
    def healthcheck(self) -> Dict[str, Any]:
        """
        Performs a health check on the FME Flow server.

        Returns:
            Dict[str, Any]: The response from the health check endpoint.

        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        return self._http_get("/healthcheck")
    
    @functools.cached_property
    def info(self) -> Dict[str, Any]:
        """
        Retrieves information about the FME Flow server.

        Returns:
            Dict[str, Any]: The response containing server information.

        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        return self._http_get("/info")
    
    @functools.cached_property
    def flow_version(self) -> str:
        """
        Retrieves the version of the FME Flow server.

        Returns:
            str: The version string of the FME Flow server.

        Raises:
            requests.HTTPError: If the HTTP request fails.
        """
        
        return self.info().get('build', 'UNKNOWN')

class AutomationsManager:
    def __init__(self, client: FMEFlowClient) -> None:
        self.client = client
        self.endpoint_base = '/automations/workflows'

    def all(self) -> List[Dict[str, Any]]:
        return self.client._http_get(f'{self.endpoint_base}')["items"]

    def tags(self) -> List[str]:
        return self.client._http_get(f'{self.endpoint_base}/tags')
    
    def get(self, workflow_id: str) -> Dict[str, Any]:
        return self.client._http_get(f'{self.endpoint_base}/{workflow_id}')
    
    def get_log(self, workflow_id: str) -> Dict[str, Any]:
        return self.client._http_get(f'{self.endpoint_base}/{workflow_id}/log')
    
    def get_status(self, workflow_id: str) -> Dict[str, Any]:
        return self.client._http_get(f'{self.endpoint_base}/{workflow_id}/status')
    

class WorkspaceManager:
    def __init__(self, client: FMEFlowClient) -> None:
        self.client = client
        self.endpoint_base = '/workspaces'

    def all(self) -> List[Dict[str, Any]]:
        repositories: Dict[str, Any] = self.client.repositories.all()
        all_workspaces: List[Dict[str, Any]] = []
        for repo in repositories:
            repo_name: Optional[str] = repo.get('name')
            if repo_name:
                workspaces: List[Dict[str, Any]] = self.client.repositories.workspaces(repo_name)
                all_workspaces.extend(workspaces)
        return all_workspaces
    
class LicensingManager:
    def __init__(self, client: FMEFlowClient) -> None:
        self.client = client
        self.endpoint_base = '/licensing'
 
    @functools.cached_property
    def capabilities(self) -> Dict[str, Any]:
        return self.client._http_get(f'{self.endpoint_base}/license/capabilities')

    @functools.cached_property
    def status(self) -> Dict[str, Any]:
        return self.client._http_get(f'{self.endpoint_base}/license/status')

    @functools.cached_property    
    def machinekey(self) -> Dict[str, Any]:
        return self.client._http_get(f'{self.endpoint_base}/machinekey')
    
    @functools.cached_property
    def systemcode(self) -> str:
        return self.client._http_get(f'{self.endpoint_base}/systemcode')["systemCode"]
    
class ProjectManager:
    def __init__(self, client: FMEFlowClient) -> None:
        self.client = client
        self.endpoint_base = '/projects'

    def all(self) -> List[Dict[str, Any]]:
        return self.client._http_get(f'{self.endpoint_base}/projects')["items"]
    
    def get(self, project_id: str) -> Dict[str, Any]:
        return self.client._http_get(f'{self.endpoint_base}/projects/{project_id}')
    
class RepositoryManager:
    def __init__(self, client: FMEFlowClient) -> None:
        self.client = client
        self.endpoint_base = '/repositories'

    def all(self) -> List[Dict[str, Any]]:
        return self.client._http_get(f'{self.endpoint_base}')["items"]
    
    def get(self, repository_name: str) -> Dict[str, Any]:
        return self.client._http_get(f'{self.endpoint_base}/{repository_name}')
    
    def workspaces(self, repository_name: str) -> List[Dict[str, Any]]:
        return self.client._http_get(f'{self.endpoint_base}/{repository_name}/items', params={"type": "WORKSPACE"})["items"]
    
