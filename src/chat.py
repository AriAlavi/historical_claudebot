from anthropic import Anthropic
from src.private_data import anthropic_api_key
from src.messenger import DiscordMessage
from typing import List
from src.personality import Personality
import discord


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
            "content": f"{message.author}: {message.content}",
        }

    def _message_is_whitespace(self, message: DiscordMessage) -> bool:
        return message.content.strip() == ""

    def _build_system_message(self) -> str:
        return {
            "role": "system",
            "content": self.personality.build_context(),
        }

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

    def build_context(self, channel: discord.TextChannel) -> str:
        personality_context = self.personality.build_context()
        server_members = [x.display_name for x in channel.guild.members]
        discord_guild_context = (
            "You can ping people with an @name_here to talk to them. Don't add punctuation to the names like commas or apostrophes. "
            "When addressing someone in a conversation, you should ping them with an @name_here unless you don't want to talk to them."
            "The following are the members of the server who you can ping to talk to: "
            + ", ".join(server_members)
        )

        return f"{personality_context}\n{discord_guild_context}"

    def build_chat_context(
        self, messages: List[DiscordMessage], channel: discord.TextChannel
    ) -> str:
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
            system=self.build_context(channel),
        )
        print("Anthropic response:", response)

        # Check if we got a response
        if not response.content:
            return "No response received from Anthropic"

        message = response.content[0].text

        if not self.personality.larping_allowed:
            message = self._remove_larping(message)

        return message
