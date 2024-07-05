from dependency_injector import containers, providers

from .services import AccountService


class Container(containers.DeclarativeContainer):

    account_service = providers.Singleton(
        AccountService,
    )
