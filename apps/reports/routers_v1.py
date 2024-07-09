from .report_router import router as report_router

routers = ({"router": report_router, "extra_params": {"tags": ("reports", )}}, )

__all__ = ("routers", )
