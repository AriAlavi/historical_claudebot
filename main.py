from src.chat import AnthropicChat
from src.discord_bot import DiscordService
from src.integrated_bot import BotService


def main():
    anthropic_client = AnthropicChat()
    discord_service = DiscordService()
    bot_service = BotService(discord_service, anthropic_client)
    bot_service.run()


if __name__ == "__main__":
    main()
