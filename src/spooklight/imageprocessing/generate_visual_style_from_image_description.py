from colorama import Back, Fore
from promptdown import StructuredPrompt

from spooklight.settings import Settings


def generate_visual_style_from_image_description(llm_client, image_description) -> str:
    """
    Generate a visual style from an image description.
    """

    print(Back.MAGENTA + "GENERATING VISUAL STYLE FROM IMAGE DESCRIPTION")

    print(Fore.BLUE + "Image description: " + Fore.GREEN + image_description)

    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight.imageprocessing",
        resource_name="generate_visual_style_from_image_description.prompt.md",
    )
    template_values = {"image_description": image_description}
    structured_prompt.apply_template_values(template_values)
    messages = structured_prompt.to_chat_completion_messages()

    response = llm_client.chat.completions.create(
        model=Settings.get_generate_visual_style_model(),
        messages=messages,
        temperature=1,
        max_tokens=200,
    )

    visual_style = response.choices[0].message.content

    print(Fore.BLUE + "Visual style: " + Fore.YELLOW + visual_style)

    return visual_style
