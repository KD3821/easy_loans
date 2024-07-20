from dependency_injector import providers, containers

from .cases import RiskCases
from .storages import RiskStorage


class Container(containers.DeclarativeContainer):
    risk_storage = providers.Singleton(
        RiskStorage,
    )

    risk_cases = providers.Singleton(
        RiskCases,
        risk_repo=risk_storage,
    )
