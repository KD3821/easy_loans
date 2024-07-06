from .customer_router import router as customer_router

routers = ({"router": customer_router, "extra_params": {"tags": ("customers", )}}, )

__all__ = ("routers", )
