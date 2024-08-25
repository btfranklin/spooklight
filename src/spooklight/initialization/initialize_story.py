from openai import OpenAI
from model import Story
from colorama import Back, Fore

from spooklight.initialization.enhance_story_concept import (
    enhance_story_concept,
)
from spooklight.initialization.generate_story_concept_from_image_description import (
    generate_story_concept_from_image_description,
)
from spooklight.imageprocessing.describe_image import describe_image_at_path


def initialize_story(
    *,
    llm_client: OpenAI,
    story_concept: str | None,
    starting_image_path: str | None,
    starting_image_description: str | None,
) -> Story:
    """
    Initialize the story with the given concept and starting point.

    If neither the `starting-image-path` nor the `starting-image-description` parameter are provided, the tool will use the story concept to generate an image description, and then use that description to generate the first image in the story. If the story concept has not been provided in this case, the tool will exit with an error.
    """

    print(Back.BLUE + "INITIALIZING STORY")

    story = Story()

    # Case 1: No story concept provided
    if story_concept is None:

        if starting_image_path is not None:
            print(
                Fore.YELLOW
                + f"Generating image description from image path: {starting_image_path}"
            )
            image_description = describe_image_at_path(llm_client, starting_image_path)

        elif starting_image_description is not None:
            print(Fore.YELLOW + "Using provided image description")
            image_description = starting_image_description

        else:
            print(
                Fore.RED
                + "ERROR: No story concept provided and no starting image path or description provided."
            )
            exit(1)

        # Now we have a description of the image that will inspire the story.
        # Let's generate the story concept from that description.
        story.concept = generate_story_concept_from_image_description(
            llm_client, image_description
        )

    # Case 2: Story concept provided
    else:

        print(Fore.YELLOW + "Using provided story concept")

        # Enhance the story concept with an LLM
        story.concept = enhance_story_concept(llm_client, story_concept)

    return story
