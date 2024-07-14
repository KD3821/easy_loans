from ..models import Report as ReportModel


class ReportStorage:
    _table = ReportModel

    @classmethod
    async def generate_report(cls, data):
        pass
