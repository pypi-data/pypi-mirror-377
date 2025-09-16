from typing import Optional

from ...direct import DirectDelivery


class WhatsappDirect(DirectDelivery):

    def __init__(
            self,
            event: str,
            recipient: str,
            params: Optional[dict] = None,
    ):
        super().__init__(
            event,
            recipient,
            params or {}
        )

        self.params = params or {}

    def build_payload(self) -> dict:
        return {
            "event": self.event,
            "recipient": self.recipient,
            "params": self.params
        }