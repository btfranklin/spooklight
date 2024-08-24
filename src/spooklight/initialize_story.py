from openai import OpenAI
from colorama import Back, Fore
from model import Story
from promptdown import StructuredPrompt

from settings import Settings
from describe_image import describe_image_at_path


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

    story = Story()

    # Case 1: No story concept provided
    if story_concept is None:

        if starting_image_path is not None:
            image_description = describe_image_at_path(llm_client, starting_image_path)

        elif starting_image_description is not None:
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

        # Enhance the story concept with an LLM
        story.concept = enhance_story_concept(llm_client, story_concept)

    return story


def enhance_story_concept(llm_client: OpenAI, story_concept: str) -> str:
    """
    Enhance the story concept with an LLM.
    """
    print(Back.BLUE + "ENHANCING STORY CONCEPT")
    print(Fore.BLUE + "Original: " + Fore.GREEN + story_concept)

    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight", resource_name="enhance_story_concept.prompt.md"
    )
    template_values = {"story_concept": story_concept}
    structured_prompt.apply_template_values(template_values)
    messages = structured_prompt.to_chat_completion_messages()

    response = llm_client.chat.completions.create(
        model=Settings.get_enhance_story_concept_model(),
        messages=messages,
        temperature=0.2,
        max_tokens=200,
    )

    enhanced_concept = response.choices[0].message.content

    print(Fore.BLUE + "Enhanced: " + Fore.YELLOW + enhanced_concept)

    return enhanced_concept


def generate_story_concept_from_image_description(llm_client, image_description) -> str:
    """
    Generate a story concept from an image description.
    """
    print(Back.BLUE + "GENERATING STORY CONCEPT")
    print(Fore.BLUE + "Image description: " + Fore.GREEN + image_description)

    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight",
        resource_name="generate_story_concept_from_image_description.prompt.md",
    )
    template_values = {"image_description": image_description}
    structured_prompt.apply_template_values(template_values)
    messages = structured_prompt.to_chat_completion_messages()

    response = llm_client.chat.completions.create(
        model=Settings.get_generate_story_concept_from_image_description_model(),
        messages=messages,
        temperature=1,
        max_tokens=100,
    )

    story_concept = response.choices[0].message.content

    print(Fore.BLUE + "Generated concept: " + Fore.YELLOW + story_concept)

    return story_concept
