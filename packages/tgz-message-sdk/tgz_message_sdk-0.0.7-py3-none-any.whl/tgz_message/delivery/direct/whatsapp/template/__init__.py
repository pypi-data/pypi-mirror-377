from abc import ABC

from ....direct import DirectDelivery

class DirectTemplateMessage(DirectDelivery, ABC):

    message_type: str = "template"
    template_type: str

    def __init__(self, recipient: str):
        super().__init__(recipient)
