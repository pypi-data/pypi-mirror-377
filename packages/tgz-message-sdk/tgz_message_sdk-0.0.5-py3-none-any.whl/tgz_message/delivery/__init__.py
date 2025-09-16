from abc import ABC, abstractmethod


class BaseDelivery(ABC):
    """
    Abstract base for all delivery types.
    """

    delivery_type: str

    @property
    def get_delivery(self):
        return self.delivery_type

    @abstractmethod
    def build_payload(self) -> dict:
        pass
