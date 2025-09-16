from typing import Optional

from ...broadcast import BroadCastDelivery


class WhatsappBroadcast(BroadCastDelivery):

    def __init__(
            self,
            event: str,
            recipients: list[str],
            params: Optional[dict] = None
    ):
        super().__init__(
            event,
            recipients,
            params or {}
        )

        self.params = params or {}

    def build_payload(self) -> dict:
        return {
            "event": self.event,
            "recipients": self.recipients,
            "params": self.params
        }