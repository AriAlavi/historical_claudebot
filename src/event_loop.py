import asyncio
import threading


class SharedEventLoop:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = SharedEventLoop()
        return cls._instance

    def __init__(self):
        self.loop = None
        self.thread = None
        self._ready = threading.Event()

    def start(self):
        if self.loop is not None:
            return

        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self._ready.set()
            self.loop.run_forever()

        self.thread = threading.Thread(target=run_loop)
        self.thread.start()
        self._ready.wait()  # Wait for loop to be ready

    def stop(self):
        if self.loop is not None:
            # Schedule the loop to stop
            self.loop.call_soon_threadsafe(self.loop.stop)
            if self.thread is not None:
                self.thread.join()
                self.thread = None
            self.loop = None

    def set_loop(self, loop):
        if self.loop is None:
            self.loop = loop
