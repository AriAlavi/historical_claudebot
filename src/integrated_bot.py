from src.discord_bot import DiscordService
from src.chat import AnthropicChat
from src.messenger import Messenger, DiscordMessage
from typing import List
import discord


class BotService(Messenger):
    def __init__(self, discord_service: DiscordService, anthropic_chat: AnthropicChat):
        self.discord_service = discord_service
        self.anthropic_chat = anthropic_chat
        self.discord_service.messenger = self

    async def handle_message(
        self, message: List[DiscordMessage], channel: discord.TextChannel
    ):
        chat_context = self.anthropic_chat.build_chat_context(message, channel)
        await self.discord_service.send_message(chat_context, channel)

    def run(self):
        self.discord_service.run()
