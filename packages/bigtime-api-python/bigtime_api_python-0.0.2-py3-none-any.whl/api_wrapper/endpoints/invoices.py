from datetime import date

from pybt.api_wrapper import models
from pybt.api_wrapper.utils import format_bigtime_date


class Invoice:
    def __init__(self, method):
        self._endpoint = "Invoice"
        self._method = method

    def __call__(self, project_id: str, calculator_id: str) -> models.Invoice:
        return self.create(project_id=project_id, calculator_id=calculator_id)

    def detail(
        self, invoice_id: str = None, invoice: models.Invoice = None
    ) -> models.Invoice | models.Result:
        params = {}
        if invoice:
            params = {**invoice}
        result: models.Result = self._method(
            endpoint=(
                f"{self._endpoint}/Detail/{invoice_id}"
                if invoice_id
                else f"{self._endpoint}/Detail"
            ),
            params=params,
        )
        return models.Invoice(**result.data) if result.data else result

    def create(self, project_id: str, calculator_id: str):
        params = {"projectsid": project_id, "invoicetype": calculator_id}

        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/Create", params=params
        )
        return models.Invoice(**result.data)

    def history(self, start_date: date, end_date: date) -> list[models.Invoice]:
        params = {
            "startdt": format_bigtime_date(start_date),
            "enddt": format_bigtime_date(end_date),
        }

        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/History", params=params
        )
        return [models.Invoice(**invoice) for invoice in result.data]

    def drafts(
        self, start_date: date = None, end_date: date = None
    ) -> list[models.Invoice]:
        params = {}
        if start_date:
            params["startdt"] = format_bigtime_date(start_date)
        if end_date:
            params["enddt"] = format_bigtime_date(end_date)

        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/History", params=params
        )
        return [models.Invoice(**invoice) for invoice in result.data]

    def invoices_by_client(
        self, client_id: str, start_date: date, end_date: date
    ) -> list[models.Invoice]:
        params = {
            "clientid": client_id,
            "startdt": format_bigtime_date(start_date),
            "enddt": format_bigtime_date(end_date),
        }

        result: models.Result = self._method(
            endpoint=f"{self._endpoint}/GetInvoicesByClientId", params=params
        )
        return [models.Invoice(**invoice) for invoice in result.data]
