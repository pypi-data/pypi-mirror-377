from abc import ABC
from typing import List

from ...delivery import BaseDelivery

class BroadcastDelivery(BaseDelivery, ABC):

    delivery_type = "broadcast"

    def __init__(self, recipients: List[str]):
        self.recipients = recipients
