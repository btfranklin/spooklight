from colorama import Back, Fore
from openai import OpenAI
from promptdown import StructuredPrompt

from spooklight.model import Story
from spooklight.settings import Settings


def generate_title_from_narrative(llm_client: OpenAI, story: Story) -> str:
    """
    Generate a title for the story from the narrative.
    """

    print(Back.MAGENTA + "GENERATING TITLE")

    # Loop through the story steps and concatenate the narratives
    story_narrative = ""
    for step in story.steps:
        story_narrative += step.narrative

    # Use the image description to generate the next narrative
    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight.completion",
        resource_name="generate_title_from_narrative.prompt.md",
    )
    template_values = {
        "story_concept": story.concept,
        "story_narrative": story_narrative,
    }
    structured_prompt.apply_template_values(template_values)
    messages = structured_prompt.to_chat_completion_messages()

    response = llm_client.chat.completions.create(
        model=Settings.get_generate_title_model(),
        messages=messages,
        temperature=1,
        max_tokens=50,
    )

    title = response.choices[0].message.content

    print(Fore.BLUE + "Title: " + Fore.YELLOW + title)

    return title
