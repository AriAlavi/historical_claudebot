from src.personality import Personality
from src.discord_bot import DiscordService
from src.chat import AnthropicChat
from src.integrated_bot import BotService


class BotFactory:
    def create_bot(self, personality: Personality) -> BotService:
        anthropic_chat = AnthropicChat(personality)
        discord_service = DiscordService(personality)
        return BotService(discord_service, anthropic_chat)
