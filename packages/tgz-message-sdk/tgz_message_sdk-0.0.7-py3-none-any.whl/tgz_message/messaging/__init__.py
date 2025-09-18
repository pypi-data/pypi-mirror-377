from abc import ABC, abstractmethod
from ..client import BaseClient

class BaseMessaging(ABC):
    """
    Abstract messaging facade.
    """

    @abstractmethod
    def dispatch(self, client: BaseClient):
        pass