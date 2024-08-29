import os
import colorama
from dotenv import load_dotenv
from openai import OpenAI

from spooklight.completion.generate_title_from_narrative import (
    generate_title_from_narrative,
)
from spooklight.initialization.initialize_story import initialize_story
from spooklight.settings import Settings
from spooklight.stepgeneration.generate_first_step import generate_first_step
from spooklight.stepgeneration.generate_step import generate_step
from spooklight.completion.story_finished import story_finished
from spooklight.completion.build_pdf_from_story_files import (
    build_pdf_from_story_files,
)


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

    # Initialize the story
    story = initialize_story(
        llm_client=llm_client,
        story_concept=story_concept,
        starting_image_path=starting_image_path,
        starting_image_description=starting_image_description,
    )

    # Save the story concept to a file in the output directory with a name like "concept.txt"
    output_dir = Settings.get_output_directory()
    with open(f"{output_dir}/concept.txt", "w") as f:
        f.write(story.concept)

    # Generate the first story step
    generate_first_step(
        llm_client=llm_client,
        story=story,
        starting_image_path=starting_image_path,
        starting_image_description=starting_image_description,
    )

    # Generate the story steps until the story is finished
    while not story_finished(llm_client, story, story_length):

        # Generate the next image and narrative
        generate_step(llm_client, story)

    # Generate the story title by reading the story narrative
    story.title = generate_title_from_narrative(llm_client, story)

    # Save the title to a file in the output directory with a name like "title.txt"
    with open(f"{output_dir}/title.txt", "w") as f:
        f.write(story.title)

    # Generate a PDF from the text and image files in the output directory
    build_pdf_from_story_files()
