from dependency_injector import providers, containers

from .cases import LoanCases
from .storages import LoanStorage
from apps.reports.storages import ReportStorage


class Container(containers.DeclarativeContainer):
    loan_storage = providers.Singleton(
        LoanStorage,
    )

    report_storage = providers.Singleton(
        ReportStorage,
    )

    loan_cases = providers.Singleton(
        LoanCases,
        loan_repo=loan_storage,
        report_repo=report_storage,
    )
