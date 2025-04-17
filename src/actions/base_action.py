from abc import ABC, abstractmethod

class BaseAction(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the action with given parameters"""
        pass

    @classmethod
    def get_description(cls) -> str:
        """Return a description of what this action does"""
        pass 