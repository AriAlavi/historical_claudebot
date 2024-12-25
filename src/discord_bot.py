import discord
from threading import Thread
from src.private_data import discord_token
import datetime
from src.messenger import Messenger, DiscordMessage
from src.personality import Personality
from typing import List


class DiscordService(discord.Client):
    def __init__(self, personality: Personality):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.discord_token = discord_token(personality.name)
        super().__init__(intents=intents)
        self._main_channels = {}
        self.message_history_limit = 20
        self.messenger: Messenger = None

    def get_main_channel(self, guild: str) -> discord.TextChannel:
        """
        Get the main channel for a guild.
        """
        if guild in self._main_channels:
            return self._main_channels[guild]

        print(f"Cache miss for getting main channel in guild: {guild}")

        for channel in guild.text_channels:
            if channel.name == "general":
                print(f"Found main channel in guild: {channel}")
                self._main_channels[guild] = channel
                return channel

        # If no main channel is found, use the first text channel
        for channel in guild.text_channels:
            print(f"Using random channel in guild: {channel}")
            self._main_channels[guild] = channel
            return channel

    def run_sync(self):
        """
        Run the discord client in a separate thread.
        """
        Thread(target=self.run, args=(self.discord_token,), daemon=True).start()

    async def send_general_message(self, message: str, guild: str):
        """
        Send a message to the general channel of a guild.
        """
        print(f"Sending message {message}")
        channel = self.get_main_channel(guild)
        await channel.send(message)

    @staticmethod
    def _find_permutations_of_words(words: List[str]) -> List[str]:
        possible_display_names = []
        words = [x.lstrip("@") for x in words]
        for i in range(1, len(words)):
            possible_display_names.append(" ".join(words[0:i]))
        return possible_display_names

    async def _replace_mentions(
        self, message: str, channel: discord.TextChannel
    ) -> str:
        MAX_NUMBER_OF_WORDS_IN_A_NAME = 10
        # Find all @mentions in the message
        words = message.split()

        print("Channel members", [x.display_name for x in channel.guild.members])

        for i in range(len(words)):
            current_word = words[i]
            if not current_word.startswith("@"):
                continue

            possible_display_names = DiscordService._find_permutations_of_words(
                words[i : i + MAX_NUMBER_OF_WORDS_IN_A_NAME]
            )
            print("POSSIBLE DISPLAY NAMES", possible_display_names)
            for possible_display_name in possible_display_names:
                for member in channel.guild.members:
                    if member.display_name == possible_display_name:
                        print("MEMBER FOUND", member)
                        words[i] = member.mention
                        break

        message = " ".join(words)
        return message

    async def send_message(self, message: str, channel: discord.TextChannel):
        """
        Send a message to a specific channel.
        """
        if not message:
            return

        message = await self._replace_mentions(message, channel)

        print(f"Sending message {message}")
        await channel.send(message)

    def _strip_mentions(self, message: discord.Message) -> str:
        """
        Strip all user mentions from the message.
        """
        # Skip if there are no mentions
        if not message.mentions:
            return message.content

        cleaned_message = message.content
        for mention in message.mentions:
            cleaned_message = cleaned_message.replace(f"<@{mention.id}>", "").replace(
                f"<@!{mention.id}>", ""
            )
        return cleaned_message

    async def get_messages(
        self, channel: discord.TextChannel, hours=1
    ) -> list[DiscordMessage]:
        """
        Fetch messages from the last hour.
        """
        messages = []
        one_hour_ago = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(hours=hours)
        async for message in channel.history(
            limit=self.message_history_limit, oldest_first=False, after=one_hour_ago
        ):
            messages.append(
                DiscordMessage(
                    author=message.author.display_name,
                    content=self._strip_mentions(message).strip(),
                    directed_to_me=self.user in message.mentions,
                    sent_by_me=message.author == self.user,
                    timestamp=message.created_at,
                )
            )
        return sorted(messages, key=lambda x: x.timestamp)

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore own messages
        if message.author == self.user:
            return

        # Check if the bot was mentioned
        if self.user in message.mentions:
            # Remove all user mentions from the message
            recent_messages = await self.get_messages(message.channel)
            await self.messenger.handle_message(recent_messages, message.channel)

    def run(self):
        super().run(self.discord_token)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
