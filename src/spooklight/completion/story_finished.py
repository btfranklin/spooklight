from colorama import Back, Fore
from promptdown import StructuredPrompt
from settings import Settings
from openai import OpenAI
from spooklight.model import Story


def story_finished(llm_client: OpenAI, story: Story, story_length: int | None) -> bool:
    """
    Check if the story has reached a natural conclusion, or has reached the maximum number of steps.
    """

    if story_length is None:
        # Determine if the story's narrative has reached a natural conclusion
        return narrative_has_reached_natural_conclusion(llm_client, story)

    else:
        return len(story.steps) >= story_length


def narrative_has_reached_natural_conclusion(llm_client: OpenAI, story: Story) -> bool:
    """
    Check if the story's narrative has reached a natural conclusion.
    """
    print(Back.BLUE + "CHECKING IF NARRATIVE HAS REACHED NATURAL CONCLUSION")

    # Loop through the story steps and concatenate the narratives
    story_narrative = ""
    for step in story.steps:
        story_narrative += step.narrative

    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight.completion",
        resource_name="narrative_has_reached_natural_conclusion.prompt.md",
    )
    template_values = {
        "story_concept": story.concept,
        "story_narrative": story_narrative,
    }
    structured_prompt.apply_template_values(template_values)
    messages = structured_prompt.to_chat_completion_messages()

    response = llm_client.chat.completions.create(
        model=Settings.get_enhance_story_concept_model(),
        messages=messages,
        temperature=0.2,
        max_tokens=1,
    )

    concluded = response.choices[0].message.content == "Yes"

    print(Fore.BLUE + "Concluded: " + Fore.YELLOW + str(concluded))

    return concluded
