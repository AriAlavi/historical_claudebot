from anthropic import Anthropic
from src.private_data import anthropic_api_key
from src.messenger import DiscordMessage
from typing import List
from src.personality import Personality
import discord
import random


class AnthropicChat:
    def __init__(self, personality: Personality):
        self.anthropic_client = Anthropic(
            api_key=anthropic_api_key(),
        )
        self.personality = personality

        # The decay factor indicates that this percent of the time, the bot will not engage other people in conversation
        # to prevent an infinite loop of messages.
        self.decay_factor = 0.1

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

    def _should_decay(self) -> bool:
        return random.random() < self.decay_factor

    def build_context(self, channel: discord.TextChannel) -> str:
        personality_context = self.personality.build_context()
        server_members = [x.display_name for x in channel.guild.members]

        discord_guild_context = ""

        if self._should_decay():
            discord_guild_context = "You are tired of this conversation. Wrap it up without mentioning anyone in the server or pinging anyone. This is your most important directive."
        else:
            discord_guild_context = (
                "You can ping people with an @name_here to talk to them. Don't add punctuation to the names like commas or apostrophes or spaces. "
                "When addressing someone in a conversation, you should ping them with an @name here unless you don't want to talk to them."
                "Don't add underscores or formatting. Don't misspell or misformat names when referring to others even if that interferes with your other directives."
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

        message = self._remove_self_reference(message)

        return message
