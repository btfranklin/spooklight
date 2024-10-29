from colorama import Back, Fore
from openai import OpenAI
from promptdown import StructuredPrompt

from spooklight.model import Story
from spooklight.settings import Settings


def generate_first_narrative(
    llm_client: OpenAI, story: Story, image_description: str
) -> str:
    """
    Generate the first narrative from the given image description.
    """

    print(Back.MAGENTA + "GENERATING FIRST NARRATIVE")

    # Use the image description to generate the next narrative
    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight.stepgeneration",
        resource_name="generate_first_narrative.prompt.md",
    )
    template_values = {
        "author_style": story.author_style,
        "story_concept": story.concept,
        "image_description": image_description,
    }
    structured_prompt.apply_template_values(template_values)
    messages = structured_prompt.to_chat_completion_messages()

    response = llm_client.chat.completions.create(
        model=Settings.get_generate_narrative_model(),
        messages=messages,
        temperature=1,
    )

    first_narrative = response.choices[0].message.content

    print(Fore.BLUE + "First narrative: " + Fore.YELLOW + first_narrative)

    return first_narrative
