import asyncio
import random
from typing import Callable, Dict, Hashable, Optional, Coroutine
from collections import defaultdict


class WeightedKeySampler:
    def __init__(
        self, sampling_interval: float, output_func: Callable[[Hashable], Coroutine]
    ):
        """
        Initialize the weighted key sampler.

        Args:
            sampling_interval: Time in seconds between sampling events
            output_func: Async function to call with the selected key when sampling
        """
        self._counts: Dict[Hashable, int] = defaultdict(int)
        self._sampling_interval = sampling_interval
        self._output_func = output_func
        self._lock = asyncio.Lock()
        self._should_stop = asyncio.Event()

    async def record_key(self, key: Hashable) -> None:
        """
        Record a call for the given key.
        Thread-safe method that can be called concurrently.

        Args:
            key: The hashable key to record
        """
        print("Recording key: ", key)
        async with self._lock:
            self._counts[key] += 1

    async def clear_count_for_key(self, key: Hashable) -> None:
        """
        Clear the count for the given key.
        """
        async with self._lock:
            if key in self._counts:
                del self._counts[key]

    async def clear_counts(self) -> None:
        """
        Clear all counts.
        """
        async with self._lock:
            self._counts.clear()

    async def _sample_and_reset(self) -> None:
        """
        Randomly select a key weighted by its count, reset counts, and call output function.
        This method is called periodically by the sampling task.
        """
        async with self._lock:
            items = list(self._counts.items())
            if not items:
                return

            keys, weights = zip(*items)
            selected_key = random.choices(keys, weights=weights, k=1)[0]

            try:
                await self._output_func(selected_key)
            except TimeoutError:
                print("TimeoutError from Claude ignored")
                # Pretend it didn't happen
                return

            del self._counts[selected_key]

    async def _sampling_loop(self) -> None:
        """
        Main loop for the sampling task.
        Performs weighted sampling at the specified interval.
        """
        print("Starting sampling loop")
        while self._running:
            await asyncio.sleep(self._sampling_interval)
            await self._sample_and_reset()

    async def run(self) -> None:
        """Main sampling loop - returns a coroutine for the caller to manage."""
        self._should_stop.clear()

        while not self._should_stop.is_set():
            await asyncio.sleep(self._sampling_interval)
            await self._sample_and_reset()

    async def stop(self) -> None:
        """Signal the sampling loop to stop."""
        self._should_stop.set()

    async def __aenter__(self):
        """Enable use as an async context manager"""
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when used as an async context manager"""
        await self.stop()
