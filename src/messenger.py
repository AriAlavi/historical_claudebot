from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
from typing import List
import discord


@dataclass
class DiscordMessage:
    author: str
    content: str
    directed_to_me: bool
    sent_by_me: bool
    timestamp: datetime

    def __str__(self):
        directed_to_me = "🎯" if self.directed_to_me else ""
        return f"{self.author}: {directed_to_me} {self.content} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"

    def __repr__(self):
        return str(self)


class Messenger(ABC):
    @abstractmethod
    async def handle_message(
        self, message: List[DiscordMessage], channel: discord.TextChannel
    ):
        pass

    @abstractmethod
    def run(self):
        pass
