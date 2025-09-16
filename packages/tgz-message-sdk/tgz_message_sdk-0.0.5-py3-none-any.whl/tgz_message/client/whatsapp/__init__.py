from ...client import BaseClient
from ...delivery import BaseDelivery

class WhatsappClient(BaseClient):

    messaging_product: str = "whatsapp"

    def __init__(self, whatsapp_delivery: BaseDelivery):
        super().__init__(whatsapp_delivery)


    def send_whatsapp_message(self, account_sid: str, auth_token:str):

        self.payload = self.delivery_type.build_payload()
        self.payload["messaging_product"] = self.messaging_product

        return self.send_api_request(
            messaging_product=self.messaging_product,
            delivery_type=self.delivery_type.get_delivery,
            account_sid=account_sid,
            auth_token=auth_token,
            payload=self.payload
        )


    def send(self, account_sid:str, auth_token:str):
        return self.send_whatsapp_message(account_sid, auth_token)