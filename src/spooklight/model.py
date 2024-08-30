class Step:
    image: bytes
    narrative: str

    def __init__(self, image: bytes, narrative: str):
        self.image = image
        self.narrative = narrative


class Story:
    title: str
    concept: str
    visual_style: str
    steps: list[Step]

    def __init__(self):
        self.title = ""
        self.concept = ""
        self.visual_style = ""
        self.steps = []
