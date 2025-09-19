from pybt.api_wrapper import models


class Task:
    def __init__(self, method):
        self._endpoint = "Task"
        self._method = method

    def detail(
        self, task_id: str = None, view: str = None, task: models.Task = None
    ) -> models.Task | models.Result:
        params = {}
        if view:
            params["view"] = view
        if task:
            params = {**task}

        result: models.Result = self._method(
            endpoint=(
                f"{self._endpoint}/Detail/{task_id}"
                if task_id
                else f"{self._endpoint}/Detail"
            ),
            params=params,
        )
        return models.Task(**result.data) if result.data else result

    def list_by_project(self, project_id: str = None, show_completed: bool = False):
        params = {}
        if show_completed:
            params["showcompleted"] = "true"

        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/ListByProject/{project_id}", params=params
        )
        return [models.Task(**task) for task in result.data]

    def budget_status_by_project(
        self, project_id: str = None
    ) -> list[models.TaskBudgetData]:
        params = {}

        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/BudgetStatusByProject/{project_id}",
            params=params,
        )
        return [models.TaskBudgetData(**budget_status) for budget_status in result.data]
