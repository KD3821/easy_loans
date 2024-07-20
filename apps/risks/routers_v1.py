from .risk_router import router as risk_router

routers = ({"router": risk_router, "extra_params": {"tags": ("risks", )}}, )

__all__ = ("routers", )
