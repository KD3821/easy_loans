from dependency_injector import containers, providers

from .cases import TransactionCases
from .storages import TransactionStorage


class Container(containers.DeclarativeContainer):
    transaction_storage = providers.Singleton(
        TransactionStorage,
    )

    transaction_cases = providers.Singleton(
        TransactionCases,
        transaction_repo=transaction_storage,
    )
