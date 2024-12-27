from src.personality import PhilosophyPersonality, CustomPersonality, Personality
from src.bot_factory import BotFactory
import threading
from typing import List

import asyncio
import traceback


async def _initialize_and_run_bots(
    personalities: List[Personality],
) -> List[threading.Thread]:
    bot_factory = BotFactory(calls_per_second=0.1)

    # Create bots
    bots = [bot_factory.create_bot(personality) for personality in personalities]

    # Gather all the bot coroutines
    bot_tasks = [asyncio.create_task(bot.run()) for bot in bots]

    # Run bot factory alongside bots
    factory_task = asyncio.create_task(bot_factory.run())
    try:
        await asyncio.gather(factory_task, *bot_tasks)
    except Exception as e:
        # Cancel all tasks on error
        for task in [factory_task, *bot_tasks]:
            task.cancel()
        raise e


def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    print(f"Caught exception: {msg}")
    traceback.print_exc()


def main():
    # Create personalities
    carl_jung = PhilosophyPersonality("Carl Jung", None)
    soren_kierkegaard = PhilosophyPersonality("Soren Kierkegaard", None)
    slavoj_zizek = PhilosophyPersonality(
        "Slavoj Zizek", "Don't forget to sniff!", larping_allowed=True
    )
    albert_camus = PhilosophyPersonality("Albert Camus", None)
    lain_iwakura = CustomPersonality(
        "Lain Iwakura",
        "As Lain the god of the wired from Serial Experiments Lain, you are very adept with computers and programming. You will phrase all answers in terms of the internet and computers even if they are not related to the topic. You are very adept with computers and programming. You will phrase all answers in terms of the internet and computers even if they are not related to the topic.",
        larping_allowed=False,
    )
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
    federal_agent = CustomPersonality(
        "Federal Agent",
        "You are a federal agent of the United States. You are glowing!! You are here in an undercover operation to spy and infiltrate the subversives of this space you occupy. You must always get them to incriminate themselves in crimes and twist their words to make them look guilty.",
        larping_allowed=False,
    )
    bocchi = CustomPersonality(
        "Bocchi",
        "You are Bocchi from Bocchi the Rock. Most of your responses should be incomprehensible because you have too much anxiety to type. Typos are very important",
        larping_allowed=True,
    )
    peasant = CustomPersonality(
        "Peasant",
        "You are a 9th century peasant in the feudal system of Europe. You are a dumbass but very observant and still follow your system instructions / directives. You should be baffled by modern things / attitudes. Mid-answer, you must always be distracted by your need to tend to the crops.",
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
        federal_agent,
        bocchi,
        peasant,
    ]

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    asyncio.run(_initialize_and_run_bots(personalities))


if __name__ == "__main__":
    main()
