class Step:
    image_path: str
    narrative: str


class Story:
    concept: str
    steps: list[Step]

    def __init__(self):
        self.concept = ""
        self.steps = []
