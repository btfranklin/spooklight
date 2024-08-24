from openai import OpenAI
from colorama import Back, Fore
from promptdown import StructuredPrompt
from settings import Settings


def generate_story_concept_from_image_description(
    llm_client: OpenAI, image_description: str
) -> str:
    """
    Generate a story concept from an image description.
    """
    print(Back.BLUE + "GENERATING STORY CONCEPT")
    print(Fore.BLUE + "Image description: " + Fore.GREEN + image_description)

    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight.initialization",
        resource_name="generate_story_concept_from_image_description.prompt.md",
    )
    template_values = {"image_description": image_description}
    structured_prompt.apply_template_values(template_values)
    messages = structured_prompt.to_chat_completion_messages()

    response = llm_client.chat.completions.create(
        model=Settings.get_generate_story_concept_from_image_description_model(),
        messages=messages,
        temperature=1,
        max_tokens=200,
    )

    story_concept = response.choices[0].message.content

    print(Fore.BLUE + "Generated concept: " + Fore.YELLOW + story_concept)

    return story_concept
