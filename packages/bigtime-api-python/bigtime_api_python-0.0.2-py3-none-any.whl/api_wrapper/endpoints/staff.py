from pybt.api_wrapper import models


class Staff:
    def __init__(self, method):
        self._endpoint = "Staff"
        self._method = method

    def __call__(self, show_inactive: bool = False) -> list[models.User]:
        params = {}
        if show_inactive:
            params["show_inactive"] = "true"
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}", params=params
        )
        return [models.User(**staff) for staff in result.data]

    def detail(
        self, staff_id: str = None, view: str = None, staff: models.User = None
    ) -> models.User | models.Result:
        params = {}
        if view:
            params["view"] = view
        if staff:
            params = {**staff}
        result: models.Result = self._method(
            endpoint=(
                f"{self._endpoint}/Detail/{staff_id}"
                if staff_id
                else f"{self._endpoint}/Detail"
            ),
            params=params,
        )
        return models.User(**result.data) if result.data else result
