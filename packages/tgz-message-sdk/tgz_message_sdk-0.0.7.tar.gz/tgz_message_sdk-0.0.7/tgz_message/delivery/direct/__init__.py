from abc import ABC

from ...delivery import BaseDelivery

class DirectDelivery(BaseDelivery, ABC):

    delivery_type = "direct"

    def __init__(self, recipient: str):
        self.recipient = recipient
