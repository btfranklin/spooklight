class Step:
    image: bytes
    narrative: str


class Story:
    concept: str
    steps: list[Step]

    def __init__(self):
        self.concept = ""
        self.steps = []
