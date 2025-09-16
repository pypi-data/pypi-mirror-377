from abc import ABC

from ...delivery import BaseDelivery

class DirectDelivery(BaseDelivery, ABC):

    delivery_type = "direct"

    def __init__(
            self,
            event: str,
            recipient: str,
            params: dict
    ):
        self.event = event
        self.recipient = recipient
        self.params = params
