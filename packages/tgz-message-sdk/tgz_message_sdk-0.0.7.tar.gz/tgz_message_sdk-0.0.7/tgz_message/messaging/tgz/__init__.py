from ...messaging import BaseMessaging
from ...client import BaseClient

class TGZMessaging(BaseMessaging):
    """
    TGZ Messaging -
    """
    def __init__(self, account_sid: str, auth_token: str):
        if not account_sid or not auth_token:
            raise RuntimeError('account_sid and auth_token are required and cannot be empty. Enter the valid credentials.')

        self.account_sid = account_sid
        self.auth_token = auth_token

    def dispatch(self, client: BaseClient):
        """

        :param client:
        :return:
        """

        if client is None:
            raise RuntimeError("Messaging requires a client class to dispatch messages. Client object cannot be None.")

        return client.send(
            account_sid=self.account_sid,
            auth_token=self.auth_token,
        )
