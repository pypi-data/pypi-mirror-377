from ...template import DirectTemplateMessage

class DirectNamedTemplateMessage(DirectTemplateMessage):

    template_type: str = "named"

    def __init__(self, recipient: str, params: dict = None):
        super().__init__(recipient)

        self.params = params or {}


    def build_payload(self) -> dict:
        return {

        }
