from enum import Enum

from pydantic import BaseModel
from fastapi import Query


class PaginationOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class Pagination(BaseModel):
    per_page: int
    page: int
    order: PaginationOrder


def pagination_params(
    page: int = Query(ge=1, le=50000, required=False, default=1),
    per_page: int = Query(ge=1, le=10, required=False, default=10),
    order: PaginationOrder = PaginationOrder.DESC
):
    return Pagination(per_page=per_page, page=page, order=order.value)
