from openai import OpenAI
from colorama import Back, Fore

from spooklight.imageprocessing.generate_image_from_description import (
    generate_image_from_description,
)
from spooklight.imageprocessing.describe_image import (
    describe_image_at_path,
    read_image,
)
from spooklight.imageprocessing.reencode_image import reencode_image
from spooklight.model import Step, Story
from spooklight.stepgeneration.generate_first_image_description import (
    generate_first_image_description,
)
from spooklight.stepgeneration.generate_first_narrative import generate_first_narrative
from spooklight.stepgeneration.save_step_files import save_step_files


def generate_first_step(
    *,
    llm_client: OpenAI,
    story: Story,
    starting_image_path: str | None,
    starting_image_description: str | None,
) -> None:
    """
    Generate the next image and narrative for the current step.
    """

    print(Back.BLUE + "GENERATING FIRST STEP")

    if starting_image_path is not None:
        print(Fore.YELLOW + "Using image at provided path")
        first_image = reencode_image(read_image(starting_image_path))
        image_description = describe_image_at_path(llm_client, starting_image_path)

    elif starting_image_description is not None:
        print(Fore.YELLOW + "Using provided image description")
        image_description = starting_image_description
        first_image = generate_image_from_description(llm_client, image_description)

    else:
        # Generate the first image description
        image_description = generate_first_image_description(llm_client, story)

        # Generate the first image
        first_image = generate_image_from_description(llm_client, image_description)

    # From the image, generate the first narrative
    first_narrative = generate_first_narrative(llm_client, story, image_description)

    step = Step(first_image, first_narrative)
    story.steps.append(step)

    save_step_files(story, step)
