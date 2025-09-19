from datetime import date

from pybt.api_wrapper.endpoints import (
    Picklist,
    Project,
    Report,
    Client,
    Expense,
    Task,
    Time,
    Staff,
    Invoice,
)
from pybt.api_wrapper.utils import PicklistFieldValueChoices


class Get:
    def __init__(self, rest_adapter):
        self.client = self._GetClient(rest_adapter)
        self.expense = self._GetExpense(rest_adapter)
        self.invoice = self._GetInvoice(rest_adapter)
        # self.payment = self._GetPayment(rest_adapter) # Not Implemented
        self.picklist = self._GetPicklist(rest_adapter)
        self.project = self._GetProject(rest_adapter)
        self.report = self._GetReport(rest_adapter)
        self.staff = self._GetStaff(rest_adapter)
        self.task = self._GetTask(rest_adapter)
        self.time = self._GetTime(rest_adapter)

    class _GetClient:
        def __init__(self, rest_adapter):
            self._client = Client(rest_adapter.get)

        def __call__(self, show_inactive: bool = False):
            return self._client(show_inactive=show_inactive)

        def detail(self, client_id: str, view: str = "Basic"):
            return self._client.detail(client_id=client_id, view=view)

    class _GetExpense:
        def __init__(self, rest_adapter):
            self._expense = Expense(rest_adapter.get)
            self._get_from_post = Expense(rest_adapter.post)

        def detail(self, expense_id: str):
            return self._expense.detail(expense_id=expense_id)

        # This endpoint does not work with BigTime. If report_id == 0, it returns a 200 status, but if report_id is anything else, it returns an internal server error
        # def report(
        #     self, report_id: str = "0", staff_id: str = None, view: str = "Basic"
        # ):
        #     return self._get_from_post._report(report_id=report_id, staff_id=staff_id, view=view)

        def report_by_filter(
            self,
            start_date: date = None,
            end_date: date = None,
            staff_ids: list[str] = None,
            project_ids: list[str] = None,
            view: str = "Basic",
            show_approval: bool = False,
        ):
            return self._get_from_post.report_by_filter(
                start_date=start_date,
                end_date=end_date,
                staff_ids=staff_ids,
                project_ids=project_ids,
                view=view,
                show_approval=show_approval,
            )

        def reports(self, staff_id: str = None, show_all: bool = False):
            return self._expense.reports(staff_id=staff_id, show_all=show_all)

    class _GetInvoice:
        def __init__(self, rest_adapter):
            self._invoice = Invoice(rest_adapter.get)

        def history(self, start_date: date, end_date: date):
            return self._invoice.history(start_date=start_date, end_date=end_date)

        def drafts(self, start_date: date = None, end_date: date = None):
            return self._invoice.drafts(start_date=start_date, end_date=end_date)

        def by_client(
            self, client_id: str, start_date: date = None, end_date: date = None
        ):
            return self._invoice.invoices_by_client(
                client_id=client_id, start_date=start_date, end_date=end_date
            )

        def detail(self, invoice_id: str):
            return self._invoice.detail(invoice_id=invoice_id)

    # Not Implemented
    # class _GetPayment:
    #     def __init__(self, rest_adapter):
    #         self._payment = Payment(rest_adapter)

    class _GetPicklist:
        def __init__(self, rest_adapter):
            self._picklist = Picklist(rest_adapter.get)

        def projects(self, staff_sid: str = None):
            return self._picklist.projects(staff_sid=staff_sid)

        def clients(self):
            return self._picklist.clients()

        def staff(self, show_inactive: bool = False):
            return self._picklist.staff(show_inactive)

        def all_tasks_by_project(
            self, project_id: str, budget_type: str = None, show_inactive: bool = False
        ):
            return self._picklist.all_tasks_by_project(
                project_id, budget_type, show_inactive
            )

        def estimates_by_project(
            self,
            project_id: str,
            staff_sid: str = None,
            budget_type: str = None,
            show_inactive: bool = False,
        ):
            return self._picklist.estimates_by_project(
                project_id, staff_sid, budget_type, show_inactive
            )

        def field_value(
            self, field: PicklistFieldValueChoices, show_inactive: bool = False
        ):
            return self._picklist.field_values(
                field=field.value, show_inactive=show_inactive
            )

    class _GetProject:
        def __init__(self, rest_adapter):
            self._project = Project(rest_adapter.get)

        def __call__(self, show_inactive: bool = False):
            return self._project(show_inactive)

        def detail(
            self, project_id: str, view: str = "Basic", show_all_contacts: bool = False
        ):
            return self._project.detail(project_id, view, show_all_contacts)

        def contacts(self, project_id: str):
            return self._project.contacts(project_id)

        def contact(self, project_id: str, contact_id: str):
            return self._project.contact(project_id=project_id, contact_id=contact_id)

        def team(self, project_id: str):
            return self._project.team(project_id=project_id)

    class _GetReport:
        def __init__(self, rest_adapter):
            self._report = Report(rest_adapter.get)

        def __call__(self, report_id):
            return self._report.data(report_id=report_id)

    class _GetStaff:
        def __init__(self, rest_adapter):
            self._staff = Staff(rest_adapter.get)

        def __call__(self, show_inactive: bool = False):
            return self._staff(show_inactive=show_inactive)

        def detail(self, staff_id: str, view: str = "Basic"):
            return self._staff.detail(staff_id=staff_id, view=view)

    class _GetTask:
        def __init__(self, rest_adapter):
            self._task = Task(rest_adapter.get)

        def detail(self, task_id: str, view: str = "Basic"):
            return self._task.detail(task_id=task_id, view=view)

        def list_by_project(self, project_id: str, show_completed: bool = False):
            return self._task.list_by_project(
                project_id=project_id, show_completed=show_completed
            )

        def budget_status_by_project(self, project_id: str):
            return self._task.budget_status_by_project(project_id=project_id)

    class _GetTime:
        def __init__(self, rest_adapter):
            self._time = Time(rest_adapter.get)

        def __call__(self, time_id: str):
            return self._time(time_id=time_id)

        def sheet(
            self, staff_id: str, start_date: date, end_date: date, view: str = "Basic"
        ):
            return self._time.sheet(
                staff_id=staff_id, start_date=start_date, end_date=end_date, view=view
            )

        def by_project(
            self,
            project_id: str,
            start_date: date,
            end_date: date,
            view: str = "Basic",
            is_approved: bool = False,
        ):
            return self._time.by_project(
                project_id=project_id,
                start_date=start_date,
                end_date=end_date,
                view=view,
                is_approved=is_approved,
            )
