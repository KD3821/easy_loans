from dependency_injector import containers, providers

from .cases import ReportCases
from .storages import ReportStorage, ReportSettingsStorage


class Container(containers.DeclarativeContainer):

    report_settings_storage = providers.Singleton(
        ReportSettingsStorage,
    )

    report_storage = providers.Singleton(
        ReportStorage,
    )

    report_cases = providers.Singleton(
        ReportCases,
        report_repo=report_storage,
        report_settings_repo=report_settings_storage,
    )
