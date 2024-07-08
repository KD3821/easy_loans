from .transaction_router import router as transaction_router

routers = ({"router": transaction_router, "extra_params": {"tags": ("transactions", )}}, )

__all__ = ('routers', )
