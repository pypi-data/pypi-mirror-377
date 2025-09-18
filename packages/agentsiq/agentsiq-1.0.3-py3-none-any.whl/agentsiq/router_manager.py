
from .router import ModelRouter
class RouterManager:
    _instance=None
    def __init__(self):
        self.router = ModelRouter()
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = RouterManager()
        return cls._instance
    def get(self)->ModelRouter:
        return self.router
    def reload(self):
        return self.router.reload()
    def set_strategy(self, s:str):
        return self.router.set_strategy(s)
    def set_weights(self, cost=None, latency=None, quality=None):
        return self.router.set_weights(cost, latency, quality)
router_manager = RouterManager.instance()
