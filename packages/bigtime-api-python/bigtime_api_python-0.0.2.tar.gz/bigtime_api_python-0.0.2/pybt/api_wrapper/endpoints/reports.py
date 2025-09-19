from datetime import date

from pybt.api_wrapper import models
from pybt.api_wrapper.utils import format_bigtime_date


class Report:
    def __init__(self, method):
        self._endpoint = "Report"
        self._method = method

    def data(
        self, report_id: str = None, start_date: date = None, end_date: date = None
    ) -> models.Report:
        params = {}
        if start_date:
            params["startdt"] = format_bigtime_date(start_date)
        if end_date:
            params["enddt"] = format_bigtime_date(end_date)

        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/Data/{report_id}", params=params
        )
        return models.Report(**result.data)
