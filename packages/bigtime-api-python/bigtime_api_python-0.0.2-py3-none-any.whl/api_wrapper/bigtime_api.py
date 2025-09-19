from datetime import date

from pybt.api_wrapper import models
from pybt.api_wrapper.exceptions import BigTimeAPIException
from pybt.api_wrapper.methods import Get, Create, Update, Delete
from pybt.api_wrapper.rest_adapter import RestAdapter
from pybt.api_wrapper.utils import (
    get_month_end_date,
    get_month_start_date,
    get_last_month_end_date,
    get_last_month_start_date,
    get_this_month_end_date,
    get_this_month_start_date,
    ViewChoices,
    PicklistFieldValueChoices,
)


class BigTimeAPI:
    def __init__(
        self,
        api_key: str,
        firm: str,
        hostname: str = "iq.bigtime.net/BigtimeData/api",
        ver: str = "v2",
        ssl_verify: bool = False,
    ):
        self._rest_adapter = RestAdapter(hostname, api_key, firm, ver, ssl_verify)
        self.get = Get(self._rest_adapter)
        self.create = Create(self._rest_adapter)
        self.update = Update(self._rest_adapter)
        self.delete = Delete(self._rest_adapter)

    #### Staff Timesheets

    def get_staff_timesheet(self, staff_id: str, start_date: date, end_date: date):
        return self.get.time.sheet(
            staff_id=staff_id,
            start_date=start_date,
            end_date=end_date,
            view=ViewChoices.DETAILED,
        )

    def get_month_staff_timesheet(self, staff_id: str, month: int, year: int):
        if month < 1 or month > 12:
            raise BigTimeAPIException("Only 1-12 are valid values for month")
        return self.get_staff_timesheet(
            staff_id=staff_id,
            start_date=get_month_start_date(month=month, year=year),
            end_date=get_month_end_date(month=month, year=year),
        )

    def get_this_month_staff_timesheet(self, staff_id: str):
        return self.get_staff_timesheet(
            staff_id=staff_id,
            start_date=get_this_month_start_date(),
            end_date=get_this_month_end_date(),
        )

    def get_last_month_staff_timesheet(self, staff_id: str):
        return self.get_staff_timesheet(
            staff_id=staff_id,
            start_date=get_last_month_start_date(),
            end_date=get_last_month_end_date(),
        )

    def get_all_staff_timesheets(self, start_date: date, end_date: date):
        staff_list = self.get.picklist.staff()
        return [
            self.get_staff_timesheet(
                staff_id=staff.id, start_date=start_date, end_date=end_date
            )
            for staff in staff_list
        ]

    def get_month_all_staff_timesheets(self, month: int, year: int):
        return self.get_all_staff_timesheets(
            start_date=get_month_start_date(month, year),
            end_date=get_month_end_date(month, year),
        )

    def get_this_month_all_staff_timesheets(self):
        return self.get_all_staff_timesheets(
            start_date=get_this_month_start_date(), end_date=get_this_month_end_date()
        )

    def get_last_month_all_staff_timesheets(self):
        return self.get_all_staff_timesheets(
            start_date=get_last_month_start_date(), end_date=get_last_month_end_date()
        )

    #### Project Timesheets

    def get_project_timesheet(self, project_id: str, start_date: date, end_date: date):
        return self.get.time.sheet(
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            view=ViewChoices.DETAILED,
        )

    def get_month_project_timesheet(self, project_id: str, month: int, year: int):
        if month < 1 or month > 12:
            raise BigTimeAPIException("Only 1-12 are valid values for month")
        return self.get_project_timesheet(
            project_id=project_id,
            start_date=get_month_start_date(month=month, year=year),
            end_date=get_month_end_date(month=month, year=year),
        )

    def get_this_month_project_timesheet(self, project_id: str):
        return self.get_project_timesheet(
            project_id=project_id,
            start_date=get_this_month_start_date(),
            end_date=get_this_month_end_date(),
        )

    def get_last_month_project_timesheet(self, project_id: str):
        return self.get_project_timesheet(
            project_id=project_id,
            start_date=get_last_month_start_date(),
            end_date=get_last_month_end_date(),
        )

    def get_all_project_timesheets(self, start_date: date, end_date: date):
        project_list = self.get.picklist.projects()
        return [
            self.get_project_timesheet(
                project_id=project.id, start_date=start_date, end_date=end_date
            )
            for project in project_list
        ]

    def get_month_all_project_timesheets(self, month: int, year: int):
        return self.get_all_project_timesheets(
            start_date=get_month_start_date(month, year),
            end_date=get_month_end_date(month, year),
        )

    def get_this_month_all_project_timesheets(self):
        return self.get_all_project_timesheets(
            start_date=get_this_month_start_date(), end_date=get_this_month_end_date()
        )

    def get_last_month_all_project_timesheets(self):
        return self.get_all_project_timesheets(
            start_date=get_last_month_start_date(), end_date=get_last_month_end_date()
        )

    #### Project Information

    def get_all_project_information(self, project_id: str):
        data = {
            "details": self.get.project.detail(
                project_id=project_id, view=ViewChoices.DETAILED
            ),
            "tasks": self.get.task.list_by_project(
                project_id=project_id, show_completed=True
            ),
            "team": self.get.project.team(project_id=project_id),
            "budget": self.get_project_budget_status(project_id=project_id),
            "invoices": self.get_project_invoices(project_id=project_id),
        }
        return data

    def get_project_budget_status(self, project_id: str) -> models.ProjectBudgetStatus:
        project_data = self.get.project.detail(
            project_id=project_id, view=ViewChoices.DETAILED, show_all_contacts=False
        )
        budget_status = self.get.task.budget_status_by_project(project_id=project_id)
        project_tasks = self.get.task.list_by_project(
            project_id=project_id, show_completed=False
        )

        return models.ProjectBudgetStatus(
            project=project_data,
            task_budget_list=budget_status,
            task_list=project_tasks,
        )

    def get_all_project_budget_statuses(self) -> list[models.ProjectBudgetStatus]:
        return sorted(
            [
                self.get_project_budget_status(project_id=project.id)
                for project in self.get.project(show_inactive=False)
            ],
            key=lambda k: k.total_percent_complete,
            reverse=True,
        )

    #### Invoices
    def get_project_invoices(
        self,
        project_id: str,
        start_date: date = date(year=2000, month=1, day=1),
        end_date: date = date.today(),
    ) -> list[models.Invoice]:
        invoice_list = self.get.invoice.history(
            start_date=start_date, end_date=end_date
        )
        return [invoice for invoice in invoice_list if invoice.project_id == project_id]

    def get_invoices_grouped_by_project(
        self,
        start_date: date = date(year=2000, month=1, day=1),
        end_date: date = date.today(),
    ):
        invoice_by_project = {}

        for invoice in self.get.invoice.history(
            start_date=start_date, end_date=end_date
        ):
            if invoice.project_id not in invoice_by_project.keys():
                invoice_by_project[invoice.project_id] = []
            invoice_by_project[invoice.project_id].append(invoice)

        for project in self.get.project():
            if project.id not in invoice_by_project.keys():
                invoice_by_project[project.id] = []

        return invoice_by_project

    def create_draft_invoices(self) -> dict[str, list]:
        active_billing_status_ids = [
            billing_status["Id"]
            for billing_status in self.get.picklist.field_value(
                field=PicklistFieldValueChoices.BILLING_STATUS
            )
            if billing_status["Group"] == "Active"
        ]
        data = {"drafted_invoices": [], "skipped_projects": []}
        for project in self.get.project():
            if project.billing_status_id not in active_billing_status_ids:
                data["skipped_projects"].append(
                    {
                        "project": project,
                        "reason": "Project has inactive billing status",
                    }
                )
                continue
            budget_status = self.get_project_budget_status(project_id=project.id)
            if budget_status.total_work_in_progress > 0:
                if budget_status.billable_total > budget_status.estimate_total:
                    data["skipped_projects"].append(
                        {"project": project, "reason": "Project over budget"}
                    )
                    continue
                draft_invoice = self.create.invoice(
                    project_id=project.id,
                    calculator_id=project.default_invoice_type_id,
                )
                draft_invoice.invoice_date = get_last_month_end_date()
                draft_invoice.end_date = get_last_month_end_date()
                draft_invoice.start_date = project.start_date
                updated_draft_invoice = self.update.invoice.detail(
                    invoice=draft_invoice
                )
                data["drafted_invoices"].append(updated_draft_invoice)
            else:
                data["skipped_projects"].append(
                    {"project": project, "reason": "No WIP"}
                )

        return data
