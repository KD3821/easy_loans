from dependency_injector import containers, providers

from .cases import CustomerCases
from .storages import CustomerStorage


class Container(containers.DeclarativeContainer):

    customer_storage = providers.Singleton(
        CustomerStorage
    )

    customer_cases = providers.Singleton(
        CustomerCases,
        customer_repo=customer_storage,
    )
