from dependency_injector import containers, providers

from apps.users.features.account_management.services import AccountService
from apps.users.storages import UsersStorage

from .cases import AuthCases
from .storages import SignInStorage


class Container(containers.DeclarativeContainer):

    user_storage = providers.Singleton(
        UsersStorage,
    )

    sign_in_storage = providers.Singleton(
        SignInStorage,
    )

    account_service = providers.Singleton(
        AccountService,
    )

    auth_cases = providers.Singleton(
        AuthCases,
        users_repo=user_storage,
        sign_in_repo=sign_in_storage,
        account_service=account_service,
    )
