from pybt.api_wrapper import models


class Client:
    def __init__(self, method):
        self._endpoint = "Client"
        self._method = method

    def __call__(self, show_inactive: bool = False) -> list[models.Client]:
        params = {}
        if show_inactive:
            params["show_inactive"] = "true"
        result: models.Result = self._method(
            endpoint=f"{self._endpoint}", params=params
        )
        return [models.Client(**client) for client in result.data]

    def detail(
        self, client_id: str = None, view: str = None, client: models.Client = None
    ) -> models.Client | models.Result:
        params = {}
        if view:
            params["view"] = view
        if client:
            params = {**client}
        result: models.Result = self._method(
            endpoint=(
                f"{self._endpoint}/Detail/{client_id}"
                if client_id
                else f"{self._endpoint}/Detail"
            ),
            params=params,
        )
        return models.Client(**result.data) if result.data else result
