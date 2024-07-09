from dependency_injector import containers, providers

from .cases import CustomerCases
from .storages import CustomerStorage
from apps.reports.storages import ReportSettingsStorage


class Container(containers.DeclarativeContainer):

    customer_storage = providers.Singleton(
        CustomerStorage
    )

    report_settings_storage = providers.Singleton(
        ReportSettingsStorage
    )

    customer_cases = providers.Singleton(
        CustomerCases,
        customer_repo=customer_storage,
        report_settings_repo=report_settings_storage,
    )
