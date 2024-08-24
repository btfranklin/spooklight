import click
import os
import colorama
from dotenv import load_dotenv
from openai import OpenAI

from spooklight.initialization.initialize_story import initialize_story


@click.command()
@click.option(
    "--starting-image-path",
    type=click.Path(exists=True),
    help="Path to the image that will be used as the starting point for the story.",
)
@click.option(
    "--starting-image-description",
    type=str,
    help="Description to generate the first image if no starting image path is provided.",
)
@click.option(
    "--story-concept",
    type=str,
    help="Summary of the story concept to guide the generation process.",
)
@click.option(
    "--story-length",
    type=int,
    default=None,
    help="Number of steps in the story. If not provided, the story will continue until a natural conclusion.",
)
def main(starting_image_path, starting_image_description, story_concept, story_length):
    """
    The main function for Spooklight. This function initializes the generation process,
    setting up the necessary configurations and kicking off the main generation loop.
    """

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
    # step = 0
    # while not story_finished(story, step, story_length):
    #     # 3. Generate the next image and narrative
    #     image_path, narrative = generate_step(story, step)

    #     # 4. Save the output
    #     save_output(step, image_path, narrative)

    #     # 5. Update the story state
    #     update_story(story, step, image_path, narrative)

    #     # Increment step
    #     step += 1

    # # 6. Finalize and save the story title
    # finalize_story(story)


if __name__ == "__main__":
    main()
