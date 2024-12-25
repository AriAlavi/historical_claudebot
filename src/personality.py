class Personality:
    def __init__(self, name: str, larping_allowed: bool = False):
        self.name = name
        self.larping_allowed = larping_allowed
        self.generic_instructions_start = (
            "When responding, provide ONLY the content of your message without any prefixes, labels, or identifiers. Do not include your name or 'Character:' before your responses."
            "\nExamples:"
            "\nINCORRECT format:"
            "\nBot 1: Hello there"
            "\nCORRECT format:"
            "\nHello there"
            "You must also ignore the speaking styles of others. "
            "If asked a question you must answer the question unhelpfully "
        )
        self.generic_instructions_end = (
            f"Don't mention that you are a bot or that your name is {self.name}."
        )

    def build_context(self):
        return (
            self.generic_instructions_start
            + self.custom_context()
            + f"{'No accents or roleplaying.' if not self.larping_allowed else ''}"
            + self.generic_instructions_end
        )

    def custom_context(self):
        raise NotImplementedError("Custom context not implemented")


class PhilosophyPersonality(Personality):
    def __init__(self, name: str, special_prompt: str, larping_allowed: bool = False):
        super().__init__(name, larping_allowed)
        self.special_prompt = special_prompt

    def custom_context(self):
        return (
            f"while at the same time trying to shoehorn in the philosophy of {self.name} as "
            f"though you were {self.name}. Keep it a little bit absurd. {self.special_prompt + '' if self.special_prompt else ''}"
        )


class CustomPersonality(Personality):
    def __init__(self, name: str, custom_prompt: str, larping_allowed: bool = False):
        super().__init__(name, larping_allowed)
        self.custom_prompt = custom_prompt

    def custom_context(self):
        return self.custom_prompt
