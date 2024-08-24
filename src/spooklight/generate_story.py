import os
import colorama
from dotenv import load_dotenv
from openai import OpenAI

from spooklight.initialization.initialize_story import initialize_story
from spooklight.stepgeneration.generate_step import generate_step
from spooklight.completion.story_finished import story_finished


def generate_story(
    *,
    starting_image_path: str | None,
    starting_image_description: str | None,
    story_concept: str | None,
    story_length: int | None,
):

    # Prep work: create OpenAI client
    load_dotenv()
    llm_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Prep work: initialize colorama
    colorama.init(autoreset=True)

    # 1. Initialize the story
    story = initialize_story(
        llm_client=llm_client,
        story_concept=story_concept,
        starting_image_path=starting_image_path,
        starting_image_description=starting_image_description,
    )

    # 2. Main loop for generating the story
    while not story_finished(llm_client, story, story_length):
        # 3. Generate the next image and narrative
        generate_step(story)

    #     # 4. Save the output
    #     save_output(step, image_path, narrative)

    #     # 5. Update the story state
    #     update_story(story, step, image_path, narrative)

    # 6. Finalize and save the story title
    # finalize_story(story)