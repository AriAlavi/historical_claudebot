import discord
from threading import Thread
from private_data import discord_token


class DiscordService(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.discord_token = discord_token()
        super().__init__(intents=intents)
        self._main_channels = {}

    def get_main_channel(self, guild: str) -> discord.TextChannel:
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

    async def send_message(self, message: str, guild: str):
        print(f"Sending message {message}")
        channel = self.get_main_channel(guild)
        await channel.send(message)

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore own messages
        if message.author == self.user:
            return

        # Check if the bot was mentioned
        if self.user in message.mentions:
            await self.send_message("Hello!", message.guild)

    def run(self):
        super().run(self.discord_token)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
