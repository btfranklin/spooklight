import os
from spooklight.model import Step, Story
from spooklight.settings import Settings


def save_step_files(story: Story, step: Step) -> None:
    """
    Save the step narrative and image to files in the output directory.
    """

    # Ensure that the output directory exists
    os.makedirs(Settings.get_output_directory(), exist_ok=True)

    # Save the step narrative to a file in the output directory with a name like "<step number>.txt"
    with open(
        f"{Settings.get_output_directory()}/{story.steps.index(step)}.txt", "w"
    ) as f:
        f.write(step.narrative)

    # Save the step image to a file in the output directory with a name like "<step number>.png"
    with open(
        f"{Settings.get_output_directory()}/{story.steps.index(step)}.png", "wb"
    ) as f:
        f.write(step.image)
