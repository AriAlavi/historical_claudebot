from chat import AnthropicChat
from discord_bot import DiscordService


def main():
    anthropic_client = AnthropicChat()
    discord_service = DiscordService()
    print(anthropic_client.send_message("hai"))
    discord_service.run()


if __name__ == "__main__":
    main()
