from datetime import date

from pybt.api_wrapper import models
from pybt.api_wrapper.utils import format_bigtime_date


class Time:
    def __init__(self, method):
        self._endpoint = "Time"
        self._method = method

    def __call__(
        self,
        time_id: str = None,
        time: models.Time = None,
        mark_submitted: bool = False,
    ) -> models.Time:
        params = {}
        if time:
            params = {**time}
        if mark_submitted:
            params["marksubmitted"] = "true"
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/{time_id}", params=params
        )
        return models.Time(**result.data)

    def sheet(
        self, staff_id: str, start_date: date, end_date: date, view: str = "detailed"
    ) -> models.StaffTimesheet:
        params = {
            "startdt": format_bigtime_date(start_date),
            "enddt": format_bigtime_date(end_date),
        }
        if view:
            params["view"] = view
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/Sheet/{staff_id}", params=params
        )
        return models.StaffTimesheet(
            staffSID=staff_id,
            timesheet=models.Timesheet(
                start_date=format_bigtime_date(start_date),
                end_date=format_bigtime_date(end_date),
                time_entries=[models.Time(**time) for time in result.data],
            ),
        )

    def by_project(
        self,
        project_id: str,
        start_date: date,
        end_date: date,
        view: str = "detailed",
        is_approved: bool = False,
    ) -> models.ProjectTimesheet:
        params = {
            "startdt": format_bigtime_date(start_date),
            "enddt": format_bigtime_date(end_date),
        }
        if view:
            params["view"] = view
        if is_approved:
            params["isapproved"] = "true"
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/ByProject/{project_id}", params=params
        )
        return models.ProjectTimesheet(
            projectSID=project_id,
            time_entries=[models.Time(**time) for time in result.data],
        )
