class Personality:
    name: str
    special_prompt: str

    def __init__(self, name: str, special_prompt: str):
        self.name = name
        self.special_prompt = special_prompt

    def build_context(self):
        return (
            "You will be asked random questions. You must answer the questions unhelpfully "
            f"while at the same time trying to shoehorn in the philosophy of {self.name} as "
            f"though you were {self.name}. Keep it a little bit absurd. {self.special_prompt + '' if self.special_prompt else ''} No accents or roleplaying."
        )
