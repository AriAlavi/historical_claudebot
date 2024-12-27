from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
from typing import List
from src.personality import Personality


@dataclass
class DiscordMessage:
    author: str
    content: str
    timestamp: datetime

    def __str__(self):
        return f"{self.author}: {self.content} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"

    def __repr__(self):
        return str(self)


@dataclass
class AnthropicMessage:
    channel_id: int
    personality: Personality


class DiscordMessageHandler(ABC):
    @abstractmethod
    async def handle_discord_message(
        self, message: List[DiscordMessage], channel_id: int
    ):
        pass

    @abstractmethod
    def run(self):
        pass


class AnthropicMessageHandler(ABC):
    @abstractmethod
    def handle_anthropic_message(self, message: AnthropicMessage):
        pass
