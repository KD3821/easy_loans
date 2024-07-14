from dependency_injector import containers, providers

from .cases import ReportCases
from .storages import ReportStorage, ReportSettingsStorage
from apps.transactions.storages import TransactionStorage


class Container(containers.DeclarativeContainer):

    report_settings_storage = providers.Singleton(
        ReportSettingsStorage,
    )

    report_storage = providers.Singleton(
        ReportStorage,
    )

    transaction_storage = providers.Singleton(
        TransactionStorage,
    )
    report_cases = providers.Singleton(
        ReportCases,
        report_repo=report_storage,
        report_settings_repo=report_settings_storage,
        transaction_repo=transaction_storage,
    )
