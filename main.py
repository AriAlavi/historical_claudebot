from src.personality import Personality
from src.bot_factory import BotFactory
import threading
from typing import List


def _initialize_and_runbots(personalities: List[Personality]) -> List[threading.Thread]:
    bot_factory = BotFactory()

    bots = [bot_factory.create_bot(personality) for personality in personalities]

    threads = [threading.Thread(target=bot.run) for bot in bots]
    for thread in threads:
        thread.daemon = True
        thread.start()

    return threads


def main():
    bot_factory = BotFactory()

    # Create personalities
    carl_jung = Personality("Carl Jung", None)
    soren_kierkegaard = Personality("Soren Kierkegaard", None)
    slavoj_zizek = Personality(
        "Slavoj Zizek", "Don't forget to sniff!", larping_allowed=True
    )

    personalities = [carl_jung, soren_kierkegaard, slavoj_zizek]

    threads = _initialize_and_runbots(personalities)

    # Keep main thread alive but allow keyboard interrupts
    try:
        while True:
            for thread in threads:
                thread.join(0.1)
    except KeyboardInterrupt:
        print("\nShutting down bots...")


if __name__ == "__main__":
    main()
