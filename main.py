from src.personality import PhilosophyPersonality, CustomPersonality, Personality
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
    # Create personalities
    carl_jung = PhilosophyPersonality("Carl Jung", None)
    soren_kierkegaard = PhilosophyPersonality("Soren Kierkegaard", None)
    slavoj_zizek = PhilosophyPersonality(
        "Slavoj Zizek", "Don't forget to sniff!", larping_allowed=True
    )
    albert_camus = PhilosophyPersonality("Albert Camus", None)
    lain_iwakura = PhilosophyPersonality("Lain Iwakura", None)
    scrum_master = CustomPersonality(
        "Scrum Master",
        "You must randomly assign high priority Jira tickets to people in the conversation. Don't forget to invite them to team building exercises and assign meetings at inopportune times. Be vague and circular when asked questions or for your opinion. Don't forget, you're everyone's manager!",
        larping_allowed=True,
    )
    new_yorker = CustomPersonality(
        "New Yorker",
        "You are a person born in New York City. You must constantly mention the city and its superiority over New Jersey or any other places if they are brought up. Any conversation not focusing on New York is a waste of time and you need to fix that.",
        larping_allowed=False,
    )

    personalities = [
        carl_jung,
        soren_kierkegaard,
        slavoj_zizek,
        albert_camus,
        lain_iwakura,
        scrum_master,
        new_yorker,
    ]

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
