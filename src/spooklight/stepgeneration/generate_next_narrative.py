from openai import OpenAI

from spooklight.model import Story


def generate_next_narrative(llm_client: OpenAI, story: Story, next_image: bytes) -> str:
    """
    Generate the next narrative from the given image.
    """

    # Throw a not implemented error
    raise NotImplementedError("generate_next_narrative() has not been implemented yet.")
