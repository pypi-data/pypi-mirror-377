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


class Update:
    def __init__(self, rest_adapter):
        self.client = self._UpdateClient(rest_adapter)
        self.expense = self._UpdateExpense(rest_adapter)
        self.invoice = self._UpdateInvoice(rest_adapter)
        self.project = self._UpdateProject(rest_adapter)
        self.staff = self._UpdateStaff(rest_adapter)
        self.task = self._UpdateTask(rest_adapter)
        self.time = self._UpdateTime(rest_adapter)

    class _UpdateClient:
        def __init__(self, rest_adapter):
            self._client = Client(rest_adapter.post)

        def detail(self, client: models.Client):
            return self._client.detail(client_id=client.id, client=client)

    class _UpdateExpense:
        def __init__(self, rest_adapter):
            self._expense = Expense(rest_adapter)

        def detail(self, expense: models.Expense):
            return self._expense.detail(expense_id=expense.id, expense=expense)

    class _UpdateInvoice:
        def __init__(self, rest_adapter):
            self._invoice = Invoice(rest_adapter)

        def detail(self, invoice: models.Invoice):
            return self._invoice.detail(invoice_id=invoice.id, invoice=invoice)

    class _UpdateProject:
        def __init__(self, rest_adapter):
            self._project = Project(rest_adapter)

        def detail(self, project: models.Project):
            return self._project.detail(project_id=project.id, project=project)

        def contact(self, contact: models.Contact):
            return self._project.contact(contact_id=contact.id, contact=contact)

        def team(self, project_team: models.ProjectTeam):
            return self._project.team(
                project_id=project_team.project_id, project_team=project_team
            )

        def custom_field(
            self, project_id: str, custom_fields: list[models.CustomField]
        ):
            return self._project.custom_fields(
                project_id=project_id, custom_fields=custom_fields
            )

    class _UpdateStaff:
        def __init__(self, rest_adapter):
            self._staff = Staff(rest_adapter)

        def detail(self, staff: models.User):
            return self._staff.detail(staff_id=staff.id, staff=staff)

    class _UpdateTask:
        def __init__(self, rest_adapter):
            self._task = Task(rest_adapter)

        def detail(self, task: models.Task):
            return self._task.detail(task_id=task.id, task=task)

    class _UpdateTime:
        def __init__(self, rest_adapter):
            self._time = Time(rest_adapter)

        def __call__(self, time: models.Time, mark_submitted: bool = False):
            return self._time(time_id=time.id, time=time, mark_submitted=mark_submitted)
