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

    jung_thread.start()
    kierkegaard_thread.start()

    # Wait for both threads to complete
    jung_thread.join()
    kierkegaard_thread.join()


if __name__ == "__main__":
    main()
