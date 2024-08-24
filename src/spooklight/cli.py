import click

from spooklight.generate_story import generate_story


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
    generate_story(
        starting_image_path=starting_image_path,
        starting_image_description=starting_image_description,
        story_concept=story_concept,
        story_length=story_length,
    )


if __name__ == "__main__":
    main()
