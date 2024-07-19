from dependency_injector import containers, providers

from .cases import TransactionCases
from .storages import TransactionStorage
from apps.reports.storages import RiskStorage


class Container(containers.DeclarativeContainer):
    transaction_storage = providers.Singleton(
        TransactionStorage,
    )

    risk_storage = providers.Singleton(
        RiskStorage,
    )

    transaction_cases = providers.Singleton(
        TransactionCases,
        transaction_repo=transaction_storage,
        risk_repo=risk_storage,
    )
