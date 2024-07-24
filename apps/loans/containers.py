from dependency_injector import providers, containers

from .cases import LoanCases
from .storages import LoanStorage, DecisionStorage
from apps.reports.storages import ReportStorage


class Container(containers.DeclarativeContainer):
    loan_storage = providers.Singleton(
        LoanStorage,
    )

    report_storage = providers.Singleton(
        ReportStorage,
    )

    decision_storage = providers.Singleton(
        DecisionStorage,
    )

    loan_cases = providers.Singleton(
        LoanCases,
        loan_repo=loan_storage,
        report_repo=report_storage,
        decision_repo=decision_storage,
    )
