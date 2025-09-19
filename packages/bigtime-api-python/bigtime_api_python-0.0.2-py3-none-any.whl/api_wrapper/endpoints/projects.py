from pybt.api_wrapper import models


class Project:
    def __init__(self, method):
        self._endpoint = "Project"
        self._method = method

    def __call__(self, show_inactive: bool = False) -> list[models.Project]:
        params = {}
        if show_inactive:
            params["show_inactive"] = "true"
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}", params=params
        )
        return [models.Project(**project) for project in result.data]

    def detail(
        self,
        project_id: str = None,
        view: str = None,
        show_all_contacts: bool = False,
        project: models.Project = None,
    ) -> models.Project | models.Result:
        params = {}
        if view:
            params["view"] = view
        if show_all_contacts:
            params["showallcontacts"] = "true"
        if project:
            params = {**project}
        result: models.Result = self._method(
            endpoint=(
                f"{self._endpoint}/Detail/{project_id}"
                if project_id
                else f"{self._endpoint}/Detail"
            ),
            params=params,
        )
        return (
            models.Project(**result.data)
            if result.data
            else f"{result.status_code}: {result.message}"
        )

    def contacts(self, project_id: str = None) -> list[models.Contact]:
        params = {"id": project_id}
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/Contacts", params=params
        )
        return [models.Contact(**contact) for contact in result.data]

    def contact(
        self,
        project_id: str = None,
        contact_id: str = None,
        show_all: bool = False,
        contact: models.Contact = None,
    ) -> models.Contact:
        params = {"projectsid": project_id}
        if show_all:
            params["showall"] = "true"
        if contact:
            params = {**contact}
        result: models.Result = self._method(
            endpoint=(
                f"{self._endpoint}/Contact/{contact_id}"
                if contact_id
                else f"{self._endpoint}/Contact"
            ),
            params=params,
        )
        return (
            models.Contact(**result.data)
            if result.data
            else f"{result.status_code}: {result.message}"
        )

    def team(self, project_id: str = None, project_team: models.ProjectTeam = None):
        params = {}
        if project_team:
            params = project_team.team_members
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/Team/{project_id}", params=params
        )
        return (
            models.ProjectTeam(
                [models.ProjectTeamMember(**member) for member in result.data],
                project_id,
            )
            if result.data
            else f"{result.status_code}: {result.message}"
        )

    def custom_fields(
        self, project_id: str = None, custom_fields: list[models.CustomField] = None
    ):
        params = {}
        if custom_fields:
            params = {"customfields": custom_fields}
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/CustomFields/{project_id}", params=params
        )
        return [models.CustomField(**field) for field in result.data]
