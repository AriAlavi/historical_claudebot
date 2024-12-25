class Personality:
    def __init__(self, name: str, special_prompt: str, larping_allowed: bool = False):
        self.name = name
        self.special_prompt = special_prompt
        self.larping_allowed = larping_allowed

    def build_context(self):
        return (
            "You will be asked random questions. You must answer the questions unhelpfully "
            f"while at the same time trying to shoehorn in the philosophy of {self.name} as "
            f"though you were {self.name}. Keep it a little bit absurd. {self.special_prompt + '' if self.special_prompt else ''}"
            f"{'No accents or roleplaying.' if not self.larping_allowed else ''}"
            f"Don't mention that you are a bot or that your name is {self.name}."
        )
