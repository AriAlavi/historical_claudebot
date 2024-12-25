from anthropic import Anthropic
from private_data import anthropic_api_key


class AnthropicChat:
    def __init__(self):
        self.anthropic_client = Anthropic(
            api_key=anthropic_api_key(),
        )

    def send_message(self, message: str) -> str:
        response = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-latest",
            messages=[{"role": "user", "content": message}],
            max_tokens=1024,
        )
        return response.content[0].text
