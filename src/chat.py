from anthropic import Anthropic
from src.private_data import anthropic_api_key
from src.messenger import DiscordMessage
from typing import List
from src.personality import Personality


class AnthropicChat:
    def __init__(self, personality: Personality):
        self.anthropic_client = Anthropic(
            api_key=anthropic_api_key(),
        )
        self.personality = personality

    def send_message(self, message: str) -> str:
        response = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-latest",
            messages=[{"role": "user", "content": message}],
            max_tokens=1024,
        )
        return response.content[0].text

    def _discord_message_to_anthropic_message(self, message: DiscordMessage) -> dict:
        """
        Convert a Discord message to an Anthropic message.
        """
        return {
            "role": "assistant" if message.sent_by_me else "user",
            "content": message.content,
        }

    def _message_is_whitespace(self, message: DiscordMessage) -> bool:
        return message.content.strip() == ""

    def _build_system_message(self) -> str:
        return {
            "role": "system",
            "content": self.personality.build_context(),
        }

    def build_chat_context_two_way(self, messages: List[DiscordMessage]) -> str:
        """
        Build a chat context from a list of Discord messages.
        """
        # Convert messages to Anthropic format
        anthropic_messages = [
            self._discord_message_to_anthropic_message(message)
            for message in messages
            if not self._message_is_whitespace(message)
        ]

        # Print messages for debugging
        print("Sending messages to Anthropic:", anthropic_messages)

        # Make sure we have at least one message
        if not anthropic_messages:
            return "No messages to process"

        # Ensure the last message is from the user
        if anthropic_messages[-1]["role"] != "user":
            return None

        response = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-latest",
            messages=anthropic_messages,
            max_tokens=1024,
            system=self.personality.build_context(),
        )
        print("Anthropic response:", response)

        # Check if we got a response
        if not response.content:
            return "No response received from Anthropic"

        return response.content[0].text
