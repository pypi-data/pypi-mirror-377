from ....direct import DirectDelivery


class EventMessage(DirectDelivery):

    message_type = "event"

    def __init__(self, event: str, recipient: str, params:dict = None):

        super().__init__(recipient)

        self.event = event
        self.params = params or {}


    def build_payload(self) -> dict:
        return {
            "event": self.event,
            "recipient": self.recipient,
            "params": self.params,
        }