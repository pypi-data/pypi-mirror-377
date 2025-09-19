from pybt.api_wrapper import models
from pybt.api_wrapper.exceptions import BigTimeAPIException
from pybt.api_wrapper.utils import PicklistFieldValueChoices


class Picklist:
    def __init__(self, method):
        self._endpoint = "Picklist"
        self._method = method

    def projects(self, staff_sid: str = None) -> list[models.PicklistProject]:
        """
        Get a list of projects that the current user has permissions to see.
        BigTime API docs say that you can include staffsid to see only projects that staffer is on,
        but testing shows that it only returns a list of all projects that the current user can see
        regardless of if the staffsid is included or not.
        """
        params = {}
        if staff_sid:
            params["staffsid"] = staff_sid
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/Projects", params=params
        )
        return [models.PicklistProject(**project) for project in result.data]

    def clients(self):
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/Clients", params=None
        )
        return result  # modify to put data into model class before returning

    def staff(self, show_inactive: bool = False):
        params = {}
        if show_inactive:
            params["showinactive"] = "true"
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/Staff", params=params
        )
        return [models.PicklistStaff(**staff) for staff in result.data]

    def all_tasks_by_project(
        self,
        project_sid: str,
        budget_type: str = None,
        show_inactive: bool = False,
    ):
        params = {}
        if budget_type:
            params["budgettype"] = budget_type
        if show_inactive:
            params["showinactive"] = "true"

        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/AllTasksByProject/{project_sid}", params=params
        )
        return result  # modify to put data into model class before returning

    def estimates_by_project(
        self,
        project_sid: str,
        staff_sid: str = None,
        budget_type: str = None,
        show_inactive: bool = False,
    ):
        params = {}
        if staff_sid:
            params["staffsid"] = staff_sid
        if budget_type:
            params["budgettype"] = budget_type
        if show_inactive:
            params["showinactive"] = "true"

        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/EstimatesByProjects/{project_sid}",
            params=params,
        )
        return result  # modify to put data into model class before returning

    def field_values(self, field: str, show_inactive: bool = False):
        params = {}
        if show_inactive:
            params = {"showinactive": "true"}
        if field in PicklistFieldValueChoices:
            result: models.Result = self._method(
                endpoint=f"{self._endpoint}/FieldValues/{field}", params=params
            )
            return result  # modify to put data into model class before returning
        raise BigTimeAPIException()
