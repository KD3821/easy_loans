from .loan_router import router as loan_router
from .decision_router import router as decision_router

routers = (
    {"router": loan_router, "extra_params": {"tags": ("loans", )}},
    {"router": decision_router, "extra_params": {"tags": ("decisions", )}},
)

__all__ = ("routers", )
