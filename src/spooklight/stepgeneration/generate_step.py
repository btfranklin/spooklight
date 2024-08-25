import os
from colorama import Back
from openai import OpenAI
from spooklight.model import Step, Story
from spooklight.imageprocessing.generate_image_from_description import (
    generate_image_from_description,
)
from spooklight.settings import Settings
from spooklight.stepgeneration.generate_next_image_description import (
    generate_next_image_description,
)
from spooklight.stepgeneration.generate_next_narrative import generate_next_narrative


def generate_step(llm_client: OpenAI, story: Story) -> None:
    """
    Generate the next image and narrative for the current step.
    """

    print(Back.BLUE + "GENERATING STEP")

    # Generate the next image description
    image_description = generate_next_image_description(llm_client, story)

    # Generate the next image
    next_image = generate_image_from_description(llm_client, image_description)

    # From the image, generate the next narrative
    next_narrative = generate_next_narrative(llm_client, story, next_image)

    step = Step(next_image, next_narrative)
    story.steps.append(step)

    # Ensure that the output directory exists
    os.makedirs(Settings.get_output_directory(), exist_ok=True)

    # Save the step narrative to a file in the output directory with a name like "<step number>.txt"
    with open(
        f"{Settings.get_output_directory()}/{story.steps.index(step)}.txt", "w"
    ) as f:
        f.write(step.narrative)

    # Save the step image to a file in the output directory with a name like "<step number>.png"
    with open(
        f"{Settings.get_output_directory()}/{story.steps.index(step)}.png", "wb"
    ) as f:
        f.write(step.image)
