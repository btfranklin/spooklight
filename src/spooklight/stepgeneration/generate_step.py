from colorama import Back
from openai import OpenAI
from spooklight.model import Step, Story
from spooklight.imageprocessing.generate_image_from_description import (
    generate_image_from_description,
)
from spooklight.stepgeneration.generate_next_image_description import (
    generate_next_image_description,
)
from spooklight.stepgeneration.generate_next_narrative import generate_next_narrative
from spooklight.stepgeneration.save_step_files import save_step_files


def generate_step(llm_client: OpenAI, story: Story) -> None:
    """
    Generate the next image and narrative for the current step.
    """

    print(Back.BLUE + "GENERATING STEP")

    # Generate the next image description
    image_description = generate_next_image_description(llm_client, story)

    # Generate the next image
    next_image = generate_image_from_description(
        llm_client=llm_client,
        image_description=image_description,
        visual_style=story.visual_style,
    )

    # From the image, generate the next narrative
    next_narrative = generate_next_narrative(llm_client, story, next_image)

    step = Step(next_image, next_narrative)
    story.steps.append(step)

    save_step_files(story, step)
