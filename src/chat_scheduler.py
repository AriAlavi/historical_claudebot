from src.weighted_sampler import WeightedKeySampler
from src.personality import Personality
from typing import Dict
from collections import namedtuple
from src.messenger import AnthropicMessageHandler, AnthropicMessage
import asyncio

AnthropicCall = namedtuple("AnthropicCall", ["personality_name", "channel_id"])


class AnthropicScheduler:
    def __init__(self, calls_per_second: int):
        sampling_interval = 1 / calls_per_second
        self.call_storage = WeightedKeySampler(
            sampling_interval=sampling_interval, output_func=self.make_anthropic_call
        )
        self.personalities: Dict[str, Personality] = {}
        self.anthropic_message_handlers: Dict[str, AnthropicMessageHandler] = {}

    def register_anthropic_message_handler(
        self,
        personality: Personality,
        anthropic_message_handler: AnthropicMessageHandler,
    ):
        self.anthropic_message_handlers[personality.name] = anthropic_message_handler

    def _store_personality(self, personality: Personality):
        self.personalities[personality.name] = personality

    def _get_personality(self, personality_name: str) -> Personality:
        return self.personalities[personality_name]

    def request_anthropic_call(self, personality: Personality, channel_id: int):
        """
        Request an anthropic call for the given personality.

        The call will be made by the scheduler at a later time.
        """
        print(
            f"Requesting anthropic call for personality: {personality.name} to channel: {channel_id}"
        )
        self._store_personality(personality)
        self.call_storage.record_key(AnthropicCall(personality.name, channel_id))

    def make_anthropic_call(self, anthropic_call: AnthropicCall):
        """
        Make an anthropic call for the given anthropic call data
        The call will happen as soon as possible.
        """
        print(
            "Scheduling anthropic call for personality: ",
            anthropic_call.personality_name,
            "to channel: ",
            anthropic_call.channel_id,
        )
        personality = self._get_personality(anthropic_call.personality_name)
        print(
            f"Handling call for personality: {personality.name} to channel: {anthropic_call.channel_id}"
        )
        anthropic_message_handler = self.anthropic_message_handlers[
            anthropic_call.personality_name
        ]

        anthropic_message_handler.handle_anthropic_message(
            AnthropicMessage(anthropic_call.channel_id, personality)
        )

    def silence_bots(self):
        """
        Silence all bots who wish to speak.

        This will clear all pending requests to speak.
        """
        self.call_storage.clear_counts()

    def silence_bot(self, personality_name: str):
        """
        Silence a bot who wishes to speak.

        This will clear the pending request to speak for the given personality.
        """
        self.call_storage.clear_count_for_key(personality_name)

    def run(self):
        """
        Start the scheduler with the given event loop
        """
        print("Starting AnthropicScheduler")
        # Start the sampler with our new loop
        self.call_storage.start()
        print("Started call storage")



    def stop(self):
        self.call_storage.stop()
