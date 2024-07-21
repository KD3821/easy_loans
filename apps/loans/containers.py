from dependency_injector import providers, containers

from .cases import LoanCases
from .storages import LoanStorage


class Container(containers.DeclarativeContainer):
    loan_storage = providers.Singleton(
        LoanStorage,
    )

    loan_cases = providers.Singleton(
        LoanCases,
        loan_repo=loan_storage,
    )
