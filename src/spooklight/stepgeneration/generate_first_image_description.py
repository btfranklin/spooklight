from colorama import Back, Fore
from openai import OpenAI
from promptdown import StructuredPrompt

from spooklight.model import Story
from spooklight.settings import Settings


def generate_first_image_description(llm_client: OpenAI, story: Story) -> str:
    """
    Generate the first image description for the story.
    """

    print(Back.MAGENTA + "GENERATING FIRST IMAGE DESCRIPTION")

    # Loop through the story steps and concatenate the narratives
    story_narrative = ""
    for step in story.steps:
        story_narrative += step.narrative

    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight.stepgeneration",
        resource_name="generate_first_image_description.prompt.md",
    )
    template_values = {
        "story_concept": story.concept,
        "story_narrative": story_narrative,
    }
    structured_prompt.apply_template_values(template_values)
    messages = structured_prompt.to_chat_completion_messages()

    response = llm_client.chat.completions.create(
        model=Settings.get_generate_image_description_model(),
        messages=messages,
        temperature=1,
        max_tokens=400,
    )

    image_description = response.choices[0].message.content

    print(Fore.BLUE + "Image description: " + Fore.YELLOW + image_description)

    return image_description
