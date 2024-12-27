from anthropic import Anthropic
from src.private_data import anthropic_api_key
import httpx
from src.context import AnthropicContext


class AnthropicChat:
    def __init__(self):
        # Aggressive timeout settings because we will handle timeouts in the service
        # we want fresh context data for the bots
        custom_httpx_transport = httpx.HTTPTransport(retries=1)
        httpx_client = httpx.Client(
            transport=custom_httpx_transport,
            timeout=httpx.Timeout(connect=2, read=4, write=4, pool=4),
        )
        self.anthropic_client = Anthropic(
            api_key=anthropic_api_key(),
            http_client=httpx_client,  # Note: it's http_client not httpx_client
        )

    def _remove_self_reference(self, message: str) -> str:
        """
        Sometimes bots will say messages like "Bot: Hi" instead of just "Hi".
        This function removes the bot reference from the message.
        """
        return message.replace(f"{self.personality.name}:", "")

    @staticmethod
    def _remove_larping(message: str) -> str:
        """
        Remove italics from a message by removing text between asterisks.
        If there are an odd number of asterisks, returns the original message unchanged.
        """
        # Count asterisks
        if message.count("*") % 2 != 0:
            return message

        result = ""
        inside_italics = False
        for char in message:
            if char == "*":
                inside_italics = not inside_italics
            elif not inside_italics:
                result += char

        return result.replace("\n\n\n", "\n")

    def send_message(self, context: AnthropicContext) -> str:
        response = (
            self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-latest",
                messages=context.messages,
                max_tokens=1024,
                system=context.system_directive,
            )
            .content[0]
            .text
        )
        print("Anthropic response:", response)
        message = self._remove_self_reference(response)

        if not context.larping_allowed:
            message = self._remove_larping(message)

        return message
