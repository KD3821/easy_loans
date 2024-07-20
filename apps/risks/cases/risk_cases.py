from core import Pagination
from ..storages import RiskStorage
from ..schemas import RiskList, RiskCreate, Risk, RiskUpdate


class RiskCases:
    def __init__(self, risk_repo: RiskStorage):
        self._risk_repo = risk_repo

    async def get_risk(self, risk_id: int) -> Risk:
        return await self._risk_repo.get_one(risk_id)

    async def list_risks(self, pagination: Pagination) -> RiskList:
        return await self._risk_repo.get_many(pagination)

    async def create_risk(self, data: RiskCreate) -> Risk:
        return await self._risk_repo.create(data)

    async def update_risk(self, risk_id: int, data: RiskUpdate) -> Risk:
        return await self._risk_repo.update(risk_id, data)

    async def delete_risk(self, risk_id: int) -> None:
        await self._risk_repo.delete(risk_id)
