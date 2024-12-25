from src.personality import Personality
from src.bot_factory import BotFactory
import threading


def main():
    bot_factory = BotFactory()

    # Create personalities
    carl_jung = Personality("Carl Jung", None)
    soren_kierkegaard = Personality("Soren Kierkegaard", None)

    # Create bots
    carl_jung_bot = bot_factory.create_bot(carl_jung)
    soren_kierkegaard_bot = bot_factory.create_bot(soren_kierkegaard)

    # Run bots
    # Start bots in separate threads

    jung_thread = threading.Thread(target=carl_jung_bot.run)
    kierkegaard_thread = threading.Thread(target=soren_kierkegaard_bot.run)
    jung_thread.daemon = True
    kierkegaard_thread.daemon = True

    jung_thread.start()
    kierkegaard_thread.start()

    # Keep main thread alive but allow keyboard interrupts
    try:
        while True:
            jung_thread.join(0.1)
            kierkegaard_thread.join(0.1)
    except KeyboardInterrupt:
        print("\nShutting down bots...")


if __name__ == "__main__":
    main()
