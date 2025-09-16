from ....direct import DirectDelivery


class DirectDocumentMessage(DirectDelivery):

    recipient_type: str = "individual"
    recipient: str
    message_type: str = "document"

    media_id: str
    link_url: str
    filename: str
    caption: str

    def __init__(self, recipient:str, filename:str, caption:str, media_id:str=None, link_url:str=None):
        super().__init__(recipient)
        self.media_id = media_id
        self.link_url = link_url
        self.filename = filename
        self.caption = caption

    def build_payload(self) -> dict:

        return {
            "recipient_type": self.recipient_type,
            "to": self.recipient,
            "type": self.message_type,
            "document": {
                "id": self.media_id,
                "link": self.link_url,
                "filename": self.filename,
                "caption": self.caption
            }
        }
