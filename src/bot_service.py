from src.discord_bot import DiscordService
from src.chat_scheduler import AnthropicScheduler
from src.chat import AnthropicChat
from src.messenger import (
    DiscordMessage,
    AnthropicMessageHandler,
    DiscordMessageHandler,
    AnthropicMessage,
)
from src.context import ContextBuilder
from typing import List


class BotService(DiscordMessageHandler, AnthropicMessageHandler):
    def __init__(
        self,
        discord_service: DiscordService,
        anthropic_chat: AnthropicChat,
        anthropic_scheduler: AnthropicScheduler,
        context_builder: ContextBuilder,
    ):
        self.discord_service = discord_service
        self.anthropic_chat = anthropic_chat
        self.anthropic_scheduler = anthropic_scheduler
        self.context_builder = context_builder
        self.discord_service.messenger = self

    async def handle_discord_message(
        self, message: List[DiscordMessage], channel_id: int
    ):
        """
        The discord bot will call this method when a message is received.
        """
        print(
            "Handling discord message for personality: ",
            self.context_builder.personality.name,
        )
        self.anthropic_scheduler.register_anthropic_message_handler(
            self.context_builder.personality, self
        )
        self.anthropic_scheduler.request_anthropic_call(
            self.context_builder.personality, channel_id
        )

    async def handle_anthropic_message(self, message: AnthropicMessage):
        """
        The anthropic scheduler will call this method when a message must be sent.
        """
        print("Handling anthropic message")
        context = await self.context_builder.build_context(message.channel_id)
        print("Build context for personality: ", message.personality.name)
        response = self.anthropic_chat.send_message(context)
        await self.discord_service.send_message(message.channel_id, response)

    def run(self):
        self.discord_service.run()
