class Personality:
    def __init__(self, name: str, larping_allowed: bool = False):
        self.name = name
        self.larping_allowed = larping_allowed
        self.generic_instructions_start = (
            "You must not emulate the speaking styles of others and instead use your own voice. You must try to fully emulate your assigned personality. "
            "You are {self.name}. "
            "If asked a question you must answer the question unhelpfully "
        )
        self.generic_instructions_end = f"Don't mention that you are a bot or that your name is {self.name}, speak in the 1st person tense."

    def build_context(self):
        return (
            self.generic_instructions_start
            + self.custom_context()
            + self.build_larp_context()
            + self.generic_instructions_end
        )

    def build_larp_context(self):
        if self.larping_allowed:
            return ""

        return "No accents or roleplaying."

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
