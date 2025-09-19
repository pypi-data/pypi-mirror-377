from pybt.api_wrapper.endpoints import Client, Project


class Delete:
    def __init__(self, rest_adapter):
        self.client = self._DeleteClient(rest_adapter)
        self.project = self._DeleteProject(rest_adapter)

    class _DeleteClient:
        def __init__(self, rest_adapter):
            self._client = Client(rest_adapter.delete)

        def detail(self, client_id: str):
            return self._client.detail(client_id=client_id)

    class _DeleteProject:
        def __init__(self, rest_adapter):
            self._project = Project(rest_adapter.delete)

        def contact(self, project_id: str, contact_id: str):
            return self._project.contact(project_id=project_id, contact_id=contact_id)
