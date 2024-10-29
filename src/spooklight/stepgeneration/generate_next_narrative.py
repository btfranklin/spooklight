from colorama import Back, Fore
from openai import OpenAI
from promptdown import StructuredPrompt

from spooklight.imageprocessing.describe_image import (
    describe_encoded_image,
    encode_bytes_to_base64,
)
from spooklight.model import Story
from spooklight.settings import Settings


def generate_next_narrative(llm_client: OpenAI, story: Story, next_image: bytes) -> str:
    """
    Generate the next narrative from the given image.
    """

    print(Back.MAGENTA + "GENERATING NEXT NARRATIVE")

    # Generate the image description from the next image
    encoded_image = encode_bytes_to_base64(next_image)
    image_description = describe_encoded_image(llm_client, encoded_image)

    # Loop through the story steps and concatenate the narratives
    story_narrative = ""
    for step in story.steps:
        story_narrative += step.narrative

    # Use the image description to generate the next narrative
    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight.stepgeneration",
        resource_name="generate_next_narrative.prompt.md",
    )
    template_values = {
        "author_style": story.author_style,
        "story_concept": story.concept,
        "story_narrative": story_narrative,
        "image_description": image_description,
    }
    structured_prompt.apply_template_values(template_values)
    messages = structured_prompt.to_chat_completion_messages()

    response = llm_client.chat.completions.create(
        model=Settings.get_generate_narrative_model(),
        messages=messages,
        temperature=1,
    )

    next_narrative = response.choices[0].message.content

    print(Fore.BLUE + "Next narrative: " + Fore.YELLOW + next_narrative)

    return next_narrative
