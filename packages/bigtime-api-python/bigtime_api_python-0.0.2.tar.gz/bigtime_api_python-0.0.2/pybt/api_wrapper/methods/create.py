from pybt.api_wrapper import models
from pybt.api_wrapper.endpoints import (
    Client,
    Expense,
    Invoice,
    Project,
    Staff,
    Task,
    Time,
)


class Create:
    def __init__(self, rest_adapter):
        self.client = self._CreateClient(rest_adapter)
        self.expense = self._CreateExpense(rest_adapter)
        self.invoice = self._CreateInvoice(rest_adapter)
        self.project = self._CreateProject(rest_adapter)
        self.staff = self._CreateStaff(rest_adapter)
        self.task = self._CreateTask(rest_adapter)
        self.time = self._CreateTime(rest_adapter)

    class _CreateClient:
        def __init__(self, rest_adapter):
            self._client = Client(rest_adapter.post)

        def detail(self, client: models.Client):
            return self._client.detail(client=client)

    class _CreateExpense:
        def __init__(self, rest_adapter):
            self._expense = Expense(rest_adapter.post)

        def detail(self, expense: models.Expense):
            return self._expense.detail(expense=expense)

    class _CreateInvoice:
        def __init__(self, rest_adapter):
            self._invoice = Invoice(rest_adapter.post)

        def create(self, project_id: str, calculator_id: str):
            return self._invoice.create(
                project_id=project_id, calculator_id=calculator_id
            )

    class _CreateProject:
        def __init__(self, rest_adapter):
            self._project = Project(rest_adapter.post)

        def detail(self, project: models.Project):
            return self._project.detail(project=project)

        def contact(self, contact: models.Contact):
            return self._project.contact(contact=contact)

    class _CreateStaff:
        def __init__(self, rest_adapter):
            self._staff = Staff(rest_adapter.post)

        def detail(self, staff: models.User):
            return self._staff.detail(staff=staff)

    class _CreateTask:
        def __init__(self, rest_adapter):
            self._task = Task(rest_adapter.post)

        def detail(self, task: models.Task):
            return self._task.detail(task=task)

    class _CreateTime:
        def __init__(self, rest_adapter):
            self._time = Time(rest_adapter.post)

        def __call__(self, time: models.Time, mark_submitted: bool = False):
            return self._time(time=time, mark_submitted=mark_submitted)
