from .sign_in_up_router import router as sign_in_up_router

routers = ({"router": sign_in_up_router, "extra_params": {"tags": ("auth", )}}, )

__all__ = ('routers', )
