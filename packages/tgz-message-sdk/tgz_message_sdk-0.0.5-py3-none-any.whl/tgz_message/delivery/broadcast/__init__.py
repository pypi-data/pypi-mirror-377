from abc import ABC

from ...delivery import BaseDelivery

class BroadCastDelivery(BaseDelivery, ABC):

    delivery_type = "broadcast"

    def __init__(
            self,
            event: str,
            recipients: list[str],
            params: dict
    ):
        self.event = event
        self.recipients = recipients
        self.params = params