import discord
from threading import Thread
from src.private_data import discord_token


class DiscordService(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.discord_token = discord_token()
        super().__init__(intents=intents)
        self._main_channels = {}

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

    async def send_message(self, message: str, channel: discord.TextChannel):
        """
        Send a message to a specific channel.
        """
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

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore own messages
        if message.author == self.user:
            return

        # Check if the bot was mentioned
        if self.user in message.mentions:
            # Remove all user mentions from the message
            cleaned_content = self._strip_mentions(message)
            await self.send_message(cleaned_content, message.channel)

    def run(self):
        super().run(self.discord_token)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
