from typing import List

from ....broadcast import BroadcastDelivery


class BroadcastEventMessage(BroadcastDelivery):

    message_type = "event"

    def __init__(self, event: str, recipients: List[str], params:dict = None):

        super().__init__(recipients)

        self.event = event
        self.params = params or {}


    def build_payload(self) -> dict:
        return {
            "event": self.event,
            "recipients": self.recipients,
            "params": self.params,
        }
