from .account_service_router import router as account_router

routers = ({"router": account_router, "extra_params": {"tags": ("accounts", )}}, )

__all__ = ('routers', )
