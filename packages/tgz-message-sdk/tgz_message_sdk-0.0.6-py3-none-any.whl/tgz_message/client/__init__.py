from abc import ABC, abstractmethod

from ..rest.request import APIRequest
from ..delivery import BaseDelivery

class BaseClient(ABC, APIRequest):
    """
    Abstract base client.
    """

    messaging_product: str
    payload: dict

    def __init__(self, delivery_type: BaseDelivery):
        """

        :param delivery_type:
        """

        if not delivery_type:
            raise RuntimeError("Delivery type is required. Delivery type cannot be None.")

        self.delivery_type = delivery_type

    @abstractmethod
    def send(self, account_sid:str, auth_token:str):
        pass
