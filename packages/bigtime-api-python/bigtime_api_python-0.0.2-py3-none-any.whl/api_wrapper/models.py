from datetime import date

from pybt.api_wrapper.exceptions import BigTimeAPIException


class Base:
    def __repr__(self):
        return str(
            {
                key: value
                for key, value in self.__dict__.items()
                if not key.startswith("__")
                and not callable(value)
                and not callable(getattr(value, "__get__", None))
            }
        )

    def __getitem__(self, key):
        return self.__dict__[key]

    def keys(self):
        key_list = [
            key
            for key, value in self.__dict__.items()
            if not key.startswith("__")
            and not callable(value)
            and not callable(getattr(value, "__get__", None))
            and value
        ]
        return key_list


class Result(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(self, status_code: int, message: str = "", data: dict | list = None):
        self.status_code = str(status_code)
        self.message = str(message)
        self.data = data if data else None

    def __repr__(self):
        return f"{self.status_code}: {self.message}"


class CustomField(Base):
    """Holds information about a custom field in BigTime

    Attributes:
        id: the BigTime ID of the field
        name: the name of the field
        value: the value assigned to the field
    """

    def __init__(self, Sid: str = None, Name: str = None, Value: str = None, **kwargs):
        self.id: str = Sid
        self.name: str = Name
        self.value: str = Value


class Address(Base):
    """Holds address information

    Attributes:
        address: the street address (123 Main Street)
        city: the city
        state: the state (can be 2 letter abbreviation or full name)
        zip: the 5-digit zip code
        country: the country
    """

    def __init__(
        self,
        Address: str = None,
        City: str = None,
        State: str = None,
        Zip: str = None,
        Country: str = None,
        **kwargs,
    ):
        self.address = Address
        self.city = City
        self.state = State
        self.zip = Zip
        self.country = Country


class Contact(Base):
    """Holds information about a BigTime contact

    Attributes:
        id: the BigTime ID of the contact
        tag: (PRIMARY|BILLING|OTHER) tag assigned to the contact
        project_id: the project ID that the contact is attached to
        client_id: the client ID that the contact is attached to
        first_name: first name of the contact
        last_name: last name of the contact
        company_name: company name of the contact
        email: email address of the contact
        address: Address object to hold the contact's address
    """

    def __init__(
        self,
        SystemId: str = None,
        Tag: str = None,
        ProjectSid: str = None,
        ClientSid: str = None,
        FName: str = None,
        SName: str = None,
        CompanyNm: str = None,
        EMail: str = None,
        Address: Address = None,
        **kwargs,
    ):
        self.id = SystemId
        self.tag = Tag
        self.project_id = ProjectSid
        self.client_id = ClientSid
        self.first_name = FName
        self.last_name = SName
        self.company_name = CompanyNm
        self.email = EMail
        self.address = Address


class Client(Base):
    """Holds information about a BigTime client

    Attributes:
        id: the BigTime ID of the client
        name: the name of the client
    """

    def __init__(self, SystemId: str = None, Nm: str = None, **kwargs):
        self.id = SystemId
        self.name = Nm


class Project(Base):
    """Holds information about a BigTime project

    Attributes:
        id: the BigTime ID of the project
        name: the project name
        project_code: the user-changeable project ID
        type_id: the ID of the project's type
        start_date: the start date of the project
        end_date: the end date of the project (optional)
        production_status_id: the ID of the production status
        production_status_note: the production status note
        billing_status_id: the ID of the billing status
        notes: the project notes field
        is_all_staff: True if all staff can bill to the project
        is_no_charge: True if all time and expenses are non-billable
        invoice_type_id: the default invoice type
        invoice_totals_id: the default invoice totals
        contract_notes: special invoicing instructions
        invoice_notes: notes to be included on every invoice generated
        billing_rate: the billing rate type used for the project
        basic_rate: if the project uses flat rate, this is the amount of the flat rate
        qb_customer_id: the ID of the client in QuickBooks
        client_id: the ID of the client that this project belongs to
        billing_contact_id: the ID of the billing contact for the project
        contact_list: a list of contacts for the project
        address_list: a list of addresses associated with the project
        client: a Client object
        default_invoice_type_id: the ID of the default invoice type (T&M, fixed, etc)
        default_invoice_pdf_report_id: the ID of the default invoice PDF
        default_invoice_terms_id: the ID of the default invoice terms (Net 30, Net 60, etc)
        custom_fields: a list of the custom fields for the project
    """

    def __init__(
        self,
        SystemId: str = None,
        Nm: str = None,
        ProjectCode: str = None,
        TypeId: str = None,
        StartDt: str = None,
        EndDt: str = None,
        StatusProd: str = None,
        StatusProd_nt: str = None,
        StatusBill: str = None,
        Notes: str = None,
        IsAllStaff: bool = False,
        IsNoCharge: bool = False,
        InvoiceType: str = None,
        InvoiceTotals: str = None,
        ContractNotes: str = None,
        InvoiceNotes: str = None,
        BillingRate: str = None,
        BasicRate: float = None,
        QBCustomerId: str = None,
        ClientId: str = None,
        BillingContactId: str = None,
        Contact: list[Contact] = None,
        AddressList: list[Address] = None,
        Client: Client = None,
        DefaultInvoiceTypeSid: str = None,
        DefaultInvoicePdfRptSid: str = None,
        DefaultInvoiceTermSid: str = None,
        UdfList: dict = None,
        **kwargs,
    ):
        self.id = SystemId
        self.name = Nm
        self.project_code = ProjectCode
        self.type_id = TypeId
        self.start_date = date.fromisoformat(StartDt) if StartDt else StartDt
        self.end_date = date.fromisoformat(EndDt) if EndDt else EndDt
        self.production_status_id = StatusProd
        self.production_status_note = StatusProd_nt
        self.billing_status_id = StatusBill
        self.notes = Notes
        self.is_all_staff = True if IsAllStaff == "true" else False
        self.is_no_charge = True if IsNoCharge == "true" else False
        self.invoice_type_id = InvoiceType
        self.invoice_totals_id = InvoiceTotals
        self.contract_notes = ContractNotes
        self.invoice_notes = InvoiceNotes
        self.billing_rate = BillingRate
        self.basic_rate = float(BasicRate)
        self.qb_customer_id = QBCustomerId
        self.client_id = ClientId
        self.billing_contact_id = BillingContactId
        self.contact_list = Contact
        self.address_list = AddressList
        self.client = Client
        self.default_invoice_type_id = DefaultInvoiceTypeSid
        self.default_invoice_pdf_report_id = DefaultInvoicePdfRptSid
        self.default_invoice_terms_id = DefaultInvoiceTermSid
        self.custom_fields = UdfList


class ProjectCustomField(CustomField):
    """Holds information about a custom field of a project

    Attributes:
        project_id: the ID of the project
        id: the ID of the custom field
        name: the name of the custom field
        value: the value of the custom field
    """

    def __init__(
        self,
        ProjectSid: str = None,
        Sid: str = None,
        Name: str = None,
        Value: str = None,
        **kwargs,
    ):
        super().__init__(Sid, Name, Value)
        self.project_id = ProjectSid


class TaskAssignment(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(self, StaffSid: str = None, Nm: str = None, **kwargs):
        self.staff_id = StaffSid
        self.name = Nm


class Task(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        TaskSid: str = None,
        ProjectSid: str = None,
        TaskNm: str = None,
        TaskGroup: str = None,
        FullName: str = None,
        TaskType: str = None,
        TaskType_nm: str = None,
        CurrentStatus: str = None,
        TaskId: str = None,
        Priority: str = None,
        Notes: str = None,
        AssignCount: str = None,
        AssignmentList: list[TaskAssignment] = None,
        DueDt: str = None,
        StartDt: str = None,
        FeeOrExpense: str = None,
        BudgetHours: float = None,
        BudgetFees: float = None,
        BudgetExps: float = None,
        BudgetTotal: float = None,
        PerComp: str = None,
        IsArchived: bool = False,
        DefaultQBClass: str = None,
        IsSeriesMaster: bool = False,
        MasterTaskSid: str = None,
        ParentSid: str = None,
        NoCharge: bool = False,
        **kwargs,
    ):
        self.id = TaskSid
        self.project_id = ProjectSid
        self.name = TaskNm
        self.group = TaskGroup
        self.full_name = FullName
        self.type_id = TaskType
        self.type = TaskType_nm
        self.current_status = CurrentStatus
        self.task_id = TaskId
        self.priority = Priority
        self.notes = Notes
        self.number_staff_assigned = AssignCount
        self.staff_assigned = AssignmentList
        self.due_date = DueDt
        self.start_date = StartDt
        self.fee_or_expense = FeeOrExpense
        self.estimate_hours = BudgetHours
        self.estimate_fees = BudgetFees
        self.estimate_expenses = BudgetExps
        self.estimate_total = BudgetTotal
        self.percent_complete = PerComp
        self.is_archived = IsArchived
        self.default_qb_class = DefaultQBClass
        self.is_series_master = IsSeriesMaster
        self.master_task_id = MasterTaskSid
        self.parent_id = ParentSid
        self.no_charge = NoCharge


class TaskBudgetData(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        TaskSid: str = None,
        HoursInput: float = None,
        HoursBill: float = None,
        FeesInput: float = None,
        FeesCost: float = None,
        ExpensesInput: float = None,
        ExpensesBillable: float = None,
        TotalWip: float = None,
        **kwargs,
    ):
        self.task_id = TaskSid
        self.input_hours = HoursInput
        self.billable_hours = HoursBill
        self.billable_fees = FeesInput
        self.input_cost = FeesCost
        self.input_expenses = ExpensesInput
        self.billable_expenses = ExpensesBillable
        self.total_work_in_progress = TotalWip


class ProjectBudgetStatus(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        project: Project,
        task_budget_list: list[TaskBudgetData],
        task_list: list[Task],
        **kwargs,
    ):
        self.project = project
        if project.basic_rate is None:
            raise BigTimeAPIException(
                "The Project object's 'basic_rate' must not be None"
            )
        self.task_budget_list = task_budget_list
        self.task_list = task_list

        self.estimate_hours = 0
        self.estimate_expenses = 0

        for task in self.task_list:
            self.estimate_hours += task.estimate_hours
            self.estimate_expenses += task.estimate_expenses

        self.input_hours = 0
        self.billable_hours = 0
        self.input_expenses = 0
        self.billable_expenses = 0
        self.total_work_in_progress = 0

        for task in self.task_budget_list:
            self.input_hours += task.input_hours
            self.billable_hours += task.billable_hours
            self.input_expenses += task.input_expenses
            self.billable_expenses += task.billable_expenses
            self.total_work_in_progress += task.total_work_in_progress

        self.estimate_fees = self.estimate_hours * self.project.basic_rate
        self.estimate_total = self.estimate_fees + self.estimate_expenses

        self.input_fees = self.input_hours * self.project.basic_rate
        self.billable_fees = self.billable_hours * self.project.basic_rate
        self.input_total = self.input_fees + self.input_expenses
        self.billable_total = self.billable_fees + self.billable_expenses

        self.hours_percent_complete = (
            (self.billable_hours / self.estimate_hours) * 100
            if self.estimate_hours
            else -1
        )
        self.fees_percent_complete = (
            (self.billable_fees / self.estimate_fees) * 100
            if self.estimate_fees
            else -1
        )
        self.expenses_percent_complete = (
            (self.billable_expenses / self.estimate_expenses) * 100
            if self.estimate_expenses
            else -1
        )
        self.total_percent_complete = (
            (self.billable_total / self.estimate_total) * 100
            if self.estimate_total
            else -1
        )


class LineItem(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        LineNbr: str = None,
        Nm: str = None,
        Nt: str = None,
        AcctSid: str = None,
        BudgetPer: str = None,
        IsCredit: bool = False,
        IsNonTimeCharge: bool = False,
        IsTaxable: bool = False,
        QBClassSid: str = None,
        Quantity: str = None,
        Rate: str = None,
        Amt: str = None,
        SalesTaxSid: str = None,
        SubTotalSid: str = None,
        UpdatedLineNbr: str = None,
        IsDeleted: bool = False,
        AcctSidNm: str = None,
        InvoiceSid: str = None,
        LineType: str = None,
        ProjectSid: str = None,
        QBClassNm: str = None,
        SalesTaxAmt: str = None,
        SalesTaxNm: str = None,
        Source: str = None,
        **kwargs,
    ):
        self.line_number = LineNbr
        self.name = Nm
        self.nt = Nt
        self.account_id = AcctSid  # TODO Figure out what this is
        self.budget_percent = BudgetPer  # TODO Figure out what this is
        self.is_credit = IsCredit
        self.is_non_time_charge = IsNonTimeCharge
        self.is_taxable = IsTaxable
        self.qb_class_id = QBClassSid
        self.quantity = Quantity
        self.rate = Rate
        self.amount = Amt
        self.sales_tax_id = SalesTaxSid
        self.subtotal_id = SubTotalSid
        self.updated_line_number = UpdatedLineNbr
        self.is_deleted = IsDeleted
        self.account_name = AcctSidNm
        self.invoice_id = InvoiceSid
        self.type = LineType  # TODO Figure out what this is
        self.project_id = ProjectSid
        self.qb_class_name = QBClassNm
        self.sales_tax_amount = SalesTaxAmt
        self.sales_tax_name = SalesTaxNm
        self.source = Source  # TODO Figure out what this is


class Invoice(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        Sid: str = None,
        ClientSid: str = None,
        ProjectSid: str = None,
        ClientNm: str = None,
        DName: str = None,
        BillingContactId: str = None,
        Calculator: str = None,
        CanEditInvoice: bool = False,
        InvoiceNbr: str = None,
        InvoiceDt: str = None,
        InvoiceAmt: str = None,
        Subtotal: str = None,
        TotalAmt: str = None,
        PaidAmt: str = None,
        SalesTaxAmt: str = None,
        InvoiceDtSt: str = None,
        InvoiceDtEnd: str = None,
        InvoiceDtSent: str = None,
        Note1: str = None,
        Note2: str = None,
        PONumber: str = None,
        Status: str = None,
        StatusTxt: str = None,
        ARAcctSid: str = None,
        SalesTaxSid: str = None,
        TermsSid: str = None,
        InvoiceDtDue: str = None,
        PostedStatus: str = None,
        BillingAddress: Address = None,
        FirmAddress: Address = None,
        Lines: list[LineItem] = None,
        **kwargs,
    ):
        self.id = Sid
        self.client_id = ClientSid
        self.project_id = ProjectSid
        self.client_name = ClientNm
        self.display_name = DName
        self.billing_contact_id = BillingContactId
        self.calculator = Calculator
        self.can_edit_invoice = CanEditInvoice
        self.invoice_number = InvoiceNbr
        self.invoice_date = InvoiceDt
        self.invoice_amount = InvoiceAmt
        self.subtotal = Subtotal
        self.total_amount = TotalAmt
        self.paid_amount = PaidAmt
        self.sales_tax_amount = SalesTaxAmt
        self.start_date = InvoiceDtSt
        self.end_date = InvoiceDtEnd
        self.sent_date = InvoiceDtSent
        self.note_1 = Note1
        self.note_2 = Note2
        self.purchase_order_number = PONumber
        self.status_id = Status
        self.status = StatusTxt
        self.accounts_receivable_id = ARAcctSid
        self.sales_tax_id = SalesTaxSid
        self.terms_id = TermsSid
        self.due_date = InvoiceDtDue
        self.posted_status = PostedStatus
        self.billing_address = BillingAddress
        self.firm_address = FirmAddress
        self.lines = Lines


class Report(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(self, Data: list[dict] = None, FieldList: list[dict] = None, **kwargs):
        self.data = Data
        self.field_list = FieldList


class User(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        StaffSid: str = None,
        FName: str = None,
        SName: str = None,
        Email: str = None,
        **kwargs,
    ):
        self.id = StaffSid
        self.first_name = FName
        self.last_name = SName
        self.email = Email


class Rate(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        ProjectSid: str = None,
        RateValue: str = None,
        StaffSid: str = None,
        TaskSid: str = None,
        **kwargs,
    ):
        self.project_id = ProjectSid
        self.staff_id = StaffSid
        self.task_id = TaskSid
        self.value = RateValue


class ProjectTeamMember(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        StaffSid: str = None,
        ContactRole: str = None,
        TeamLead: bool = False,
        **kwargs,
    ):
        self.staff_id = StaffSid
        self.role = ContactRole
        self.team_lead = TeamLead


class ProjectTeam(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        team_members: list[ProjectTeamMember],
        project_id: str,
    ):
        self.team_members = team_members
        self.project_id = project_id


class Expense(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        SID: str = None,
        IsSubmitted: bool = False,
        RptSID: str = None,
        StaffSID: str = None,
        Dt: str = None,
        ProjectSID: str = None,
        ProjectNm: str = None,
        ClientSID: str = None,
        ClientNm: str = None,
        CatSID: str = None,
        CatNm: str = None,
        TaskSID: str = None,
        TaskNm: str = None,
        VendorSID: str = None,
        VendorNm: str = None,
        CCardSid: str = None,
        BillSid: str = None,
        NoCharge: bool = False,
        PaidByCo: bool = False,
        Nt: str = None,
        CostIN: str = None,
        CostPayable: str = None,
        CostBill: str = None,
        IsUnit: bool = False,
        UnitPrice: str = None,
        UnitRate: str = None,
        Units: str = None,
        UOM: str = None,
        DueDate: str = None,
        RefNbr: str = None,
        HasReceipt: bool = False,
        IsApproved: bool = False,
        ApprovalStatus: str = None,
        ApprovalStatusNm: str = None,
        InvoiceSid: str = None,
        IsInvoiced: bool = False,
        IsVendorExpense: bool = False,
        ExpenseReceipt=None,
        **kwargs,
    ):
        self.id = SID
        self.is_submitted = IsSubmitted
        self.report_id = RptSID
        self.staff_id = StaffSID
        self.date = Dt
        self.project_id = ProjectSID
        self.project = ProjectNm
        self.client_id = ClientSID
        self.client = ClientNm
        self.category_id = CatSID
        self.category = CatNm
        self.task_id = TaskSID
        self.task = TaskNm
        self.vendor_id = VendorSID
        self.vendor = VendorNm
        self.credit_card_id = CCardSid
        self.bill_id = BillSid
        self.no_charge = NoCharge
        self.paid_by_company = PaidByCo
        self.notes = Nt
        self.input_amount = CostIN
        self.reimbursable_amount = CostPayable
        self.billable_amount = CostBill
        self.is_unit = IsUnit
        self.unit_price = UnitPrice
        self.unit_rate = UnitRate
        self.units = Units
        self.unit_of_measure = UOM
        self.due_date = DueDate
        self.reference_number = RefNbr
        self.has_receipt = HasReceipt
        self.is_approved = IsApproved
        self.approval_status_id = ApprovalStatus
        self.approval_status = ApprovalStatusNm
        self.invoice_id = InvoiceSid
        self.is_invoiced = IsInvoiced
        self.is_vendor_expense = IsVendorExpense
        self.expense_receipt = ExpenseReceipt


class ExpenseReport(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        SID: str = None,
        RptNm: str = None,
        CreatedDt: str = None,
        SubmitDt: str = None,
        StatusId: str = None,
        StatusNm: str = None,
        **kwargs,
    ):
        self.id = SID
        self.report_name = RptNm
        self.date_created = CreatedDt
        self.date_submitted = SubmitDt
        self.status_id = StatusId
        self.status = StatusNm


class PicklistIdName(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(self, Id: str = None, Name: str = None, **kwargs):
        self.id = Id
        self.name = Name


class PicklistProject(PicklistIdName):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(self, Id: str = None, Name: str = None, Group: str = None, **kwargs):
        super().__init__(Id, Name, **kwargs)
        self.group = Group


class PicklistClient(PicklistIdName):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(self, Id: str = None, Name: str = None, **kwargs):
        super().__init__(Id, Name, **kwargs)


class PicklistStaff(PicklistIdName):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self, Id: str = None, Name: str = None, IsInactive: bool = False, **kwargs
    ):
        super().__init__(Id, Name, **kwargs)
        self.active = not IsInactive


class Time(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        SID: str = None,
        Dt: str = None,
        ProjectSID: str = None,
        StaffSID: str = None,
        TaskSID: str = None,
        Hours_IN: str = None,
        Notes: str = None,
        HoursBillable: str = None,
        ChargeBillable: str = None,
        IsNew=None,
        ProjectNm=None,
        ClientId=None,
        ClientNm=None,
        SourceNm=None,
        TaskNm=None,
        RevisionNotes=None,
        NoCharge=None,
        IsApproved=None,
        InvoiceSID=None,
        IsInvoiced=None,
        BillRate=None,
        **kwargs,
    ):
        self.id = SID
        self.is_new = IsNew
        self.date = Dt
        self.project_id = ProjectSID
        self.project = ProjectNm
        self.client_id = ClientId
        self.client = ClientNm
        self.staff_id = StaffSID
        self.staff = SourceNm
        self.task_id = TaskSID
        self.task = TaskNm
        self.input_hours = Hours_IN
        self.notes = Notes
        self.revision_notes = RevisionNotes
        self.no_charge = NoCharge
        self.is_approved = IsApproved
        self.invoice_id = InvoiceSID
        self.is_invoiced = IsInvoiced
        self.billable_hours = HoursBillable
        self.billing_rate = BillRate
        self.billable_charges = ChargeBillable


class Timesheet(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(
        self,
        start_date: str = None,
        end_date: str = None,
        time_entries: list[Time] = None,
        **kwargs,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.time_entries = time_entries

    def __repr__(self):
        timelist = []
        for time in self.time_entries:
            timelist.append(
                {
                    key: value
                    for key, value in time.__dict__.items()
                    if not key.startswith("__")
                    and not callable(value)
                    and not callable(getattr(value, "__get__", None))
                }
            )
        return str(timelist)


class ProjectTimesheet(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(self, projectSID: str = None, timesheet: Timesheet = None, **kwargs):
        self.timesheet = timesheet
        self.project_id = projectSID


class StaffTimesheet(Base):
    """Holds the result of a REST request.

    Attributes:
        status_code: the HTTP status code of the request
        message: the message of the request
        data: the data sent with the request
    """

    def __init__(self, staffSID: str = None, timesheet: Timesheet = None, **kwargs):
        self.timesheet = timesheet
        self.staff_id = staffSID


class Ticket: ...
