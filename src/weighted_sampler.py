import threading
import time
import random
import asyncio
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
            output_func: Function to call with the selected key when sampling
        """
        self._counts: Dict[Hashable, int] = defaultdict(int)
        self._lock = threading.Lock()
        self._sampling_interval = sampling_interval
        self._output_func = output_func
        self._running = False
        self._sampling_thread: Optional[threading.Thread] = None
        # Create an event loop for this thread

    def record_key(self, key: Hashable) -> None:
        """
        Record a call for the given key.
        Thread-safe method that can be called concurrently.

        Args:
            key: The hashable key to record
        """
        print("Recording key: ", key)
        with self._lock:
            self._counts[key] += 1

    def clear_count_for_key(self, key: Hashable) -> None:
        """
        Clear the count for the given key.
        """
        with self._lock:
            if key in self._counts:
                del self._counts[key]

    def clear_counts(self) -> None:
        """
        Clear all counts in a thread-safe manner.
        """
        with self._lock:
            self._counts.clear()

    def _sample_and_reset(self) -> None:
        """
        Randomly select a key weighted by its count, reset counts, and call output function.
        This method is called periodically by the sampling thread.
        """
        with self._lock:
            items = list(self._counts.items())
            if not items:
                return

            keys, weights = zip(*items)
            selected_key = random.choices(keys, weights=weights, k=1)[0]

            # Instead of awaiting directly, just schedule the task and move on
            self._output_func(selected_key)

            del self._counts[selected_key]

    def _sampling_loop(self) -> None:
        """
        Main loop for the sampling thread.
        Performs weighted sampling at the specified interval.
        """
        print("Starting sampling loop")
        while self._running:
            time.sleep(self._sampling_interval)
            self._sample_and_reset()

    def start(self) -> None:
        """
        Start the sampling thread.

        Args:
            loop: The event loop to use for async callbacks. If None, will try to get the current loop.
        """
        print("Starting weighted sampler")
        if self._sampling_thread is not None:
            print("Sampling thread already running")
            return

        self._running = True
        self._sampling_thread = threading.Thread(
            target=self._sampling_loop, daemon=True
        )
        self._sampling_thread.start()
        print("Sampling thread started")

    def stop(self) -> None:
        """
        Stop the sampling thread.
        """
        self._running = False
        if self._sampling_thread is not None:
            self._sampling_thread.join()
            self._sampling_thread = None

    def __enter__(self):
        """Enable use as a context manager"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when used as a context manager"""
        self.stop()
