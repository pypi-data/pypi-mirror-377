from abc import ABC, abstractmethod


class BaseDelivery(ABC):
    """
    Abstract base for all delivery types.
    """

    delivery_type: str
    message_type: str
    template_type: str = None

    @property
    def get_delivery(self):
        return self.delivery_type

    @property
    def get_message_type(self):
        return self.message_type

    @property
    def get_template_type(self):
        return self.template_type

    @abstractmethod
    def build_payload(self) -> dict:
        pass
