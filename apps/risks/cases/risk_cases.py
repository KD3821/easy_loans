from core import Pagination
from ..storages import RiskStorage
from ..schemas import RiskList


class RiskCases:
    def __init__(self, risk_repo: RiskStorage):
        self._risk_repo = risk_repo

    async def list_risks(self, pagination: Pagination) -> RiskList:
        return await self._risk_repo.get_many(pagination)
