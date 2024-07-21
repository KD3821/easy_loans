from .loan_router import router as loan_router

routers = ({"router": loan_router, "extra_params": {"tags": ("loans", )}}, )

__all__ = ("routers", )
