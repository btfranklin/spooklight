from colorama import Back, Fore
from promptdown import StructuredPrompt
from openai import OpenAI

from spooklight.settings import Settings


def enhance_story_concept(llm_client: OpenAI, story_concept: str) -> str:
    """
    Enhance the story concept with an LLM.
    """
    print(Back.BLUE + "ENHANCING STORY CONCEPT")
    print(Fore.BLUE + "Original: " + Fore.GREEN + story_concept)

    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight.initialization",
        resource_name="enhance_story_concept.prompt.md",
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
