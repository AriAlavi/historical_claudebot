from src.personality import Personality
from src.discord_bot import DiscordService
from src.chat import AnthropicChat
from src.bot_service import BotService
from src.chat_scheduler import AnthropicScheduler
from src.private_data import discord_token
from src.context import ContextBuilder


class BotFactory:
    def __init__(self, calls_per_second: int):
        self.anthropic_scheduler = AnthropicScheduler(calls_per_second=calls_per_second)

    def create_bot(self, personality: Personality) -> BotService:
        discord_service = DiscordService(discord_token(personality.name))
        return BotService(
            discord_service=discord_service,
            anthropic_chat=AnthropicChat(),
            anthropic_scheduler=self.anthropic_scheduler,
            context_builder=ContextBuilder(discord_service, personality),
        )

    def run(self):
        self.anthropic_scheduler.run()

    def stop(self):
        self.anthropic_scheduler.stop()
