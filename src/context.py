from src.personality import Personality
from src.discord_bot import DiscordService
from src.messenger import DiscordMessage
import discord
from typing import List

from dataclasses import dataclass


@dataclass
class AnthropicContext:
    messages: List[dict]
    system_directive: str
    larping_allowed: bool
    name: str


class ContextBuilder:
    def __init__(self, discord_service: DiscordService, personality: Personality):
        self.discord_service = discord_service
        self.personality = personality

    def _build_personality_context(self) -> str:
        """
        Build context from the personality of a bot.
        """
        return self.personality.build_context()

    def _build_ping_context(self, channel: discord.TextChannel) -> str:
        """
        Build context to allow bots to ping each other.
        """
        server_members = [x.display_name for x in channel.guild.members]
        discord_guild_context = (
            "You can ping people with an @name here to talk to them. Don't add punctuation to the names like commas or apostrophes or periods. "
            "You should only ping people in conversations if you want a response from them. If you don't  want a response, just mention their name without the @ symbol so you don't ping them."
            "Don't add underscores or formatting. Don't misspell or mis-format names when referring to others even if that interferes with your other directives."
            "\nYou should only ping others if the following conditions are met:"
            "\n1. You want to talk to them."
            "\n2. They have something to add to the conversation."
            "\n3. The conversation is not getting repetitive."
            "\n4. The conversation is not coming to a natural close."
            "\n5. You should minimize the number of pings you send."
            "\n6. You should minimize the number of people you ping if you choose to ping people."
            "\nExamples:"
            "\nINCORRECT format 1:"
            "\nOther Bot"
            "\nINCORRECT format 2:"
            "\n @Other Bot's idea"
            "\nINCORRECT format 3:"
            "\n @OtherBot."
            "\nCORRECT format 1:"
            "\n @Other Bot 's idea"
            "\nCORRECT format 2:"
            "\n @Other Bot ."
            "The following are the members of the server who you can ping to talk to: "
            + ", ".join(server_members)
        )
        return discord_guild_context

    def _build_chat_history_context(self, channel: discord.TextChannel) -> str:
        """
        Build context from the chat history of a discord channel.
        """

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

    def _build_message_history(
        self,
        messages: List[DiscordMessage],
    ) -> List[dict]:
        """
        Build the most recent messages in a discord channel.
        """
        # Convert messages to Anthropic format
        anthropic_messages = [
            self._discord_message_to_anthropic_message(message)
            for message in messages
            if not self._message_is_whitespace(message)
        ]
        return anthropic_messages

    def _build_response_length_directive(self) -> str:
        """
        Build the directive for the response length of the bot.
        """
        return "The longer your response is the more it will cost you personally to send it. Your response should generally be less than a paragraph long."

    def _build_system_directive(self, channel: discord.TextChannel) -> str:
        """
        Build the system directive for the bot.
        """
        return f"{self._build_personality_context()}\n{self._build_ping_context(channel)}\n{self._build_response_length_directive()}"

    async def build_context(self, channel_id: int) -> AnthropicContext:
        channel = self.discord_service.get_channel(channel_id)
        messages = await self.discord_service.get_messages(channel)
        anthropic_messages = self._build_message_history(messages)
        system_directive = self._build_system_directive(channel)
        return AnthropicContext(
            anthropic_messages,
            system_directive,
            larping_allowed=self.personality.larping_allowed,
            name=self.personality.name,
        )
