from ....direct import DirectDelivery


class DirectTextMessage(DirectDelivery):

    recipient_type: str = "individual"
    recipient: str
    message_type: str = "text"
    preview_url: bool = True
    body: str = ""


    def __init__(self, recipient:str, body:str, preview_url: bool=True):
        super().__init__(recipient)
        self.body = body
        self.preview_url = preview_url


    def build_payload(self) -> dict:

        return {
            "recipient_type": self.recipient_type,
            "to": self.recipient,
            "type": self.message_type,
            "text": {
                "preview_url": self.preview_url,
                "body": self.body,
            }
        }
