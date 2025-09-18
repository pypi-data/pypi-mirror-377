from ...template import DirectTemplateMessage


class DirectPositionalTemplateMessage(DirectTemplateMessage):

    template_type: str = "positional"

    def __init__(self, recipient: str, params: dict = None):
        super().__init__(recipient)

        self.params = params or {}


    def build_payload(self) -> dict:
        return {

        }
