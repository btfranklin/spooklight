from colorama import Fore
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.lib import utils
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.units import inch

from spooklight.model import Story
from spooklight.completion.generate_title_from_narrative import (
    generate_title_from_narrative,
)


def finalize_story(
    llm_client: OpenAI, story: Story, output_file: str = "output/story.pdf"
) -> None:
    """
    Finalize the story by generating a title for the story, and saving the story to a PDF file.
    """

    # Generate the story title by reading the story narrative
    story.title = generate_title_from_narrative(llm_client, story)

    # Create a PDF document
    pdf = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story_flow = []

    # Add a title page
    title_style = styles["Title"]
    story_flow.append(Paragraph(story.title, title_style))
    story_flow.append(Spacer(1, 2 * inch))  # Adds some space after the title

    # Add each step to the PDF
    for step in story.steps:
        # Add narrative
        story_flow.append(Paragraph(step.narrative, styles["BodyText"]))
        story_flow.append(Spacer(1, 0.5 * inch))  # Space between narrative and image

        # Add image
        image = utils.ImageReader(step.image)
        img_width, img_height = image.getSize()

        # Scale the image to fit the page width, maintaining aspect ratio
        max_width = letter[0] - 2 * inch
        aspect_ratio = img_height / float(img_width)
        scaled_height = max_width * aspect_ratio
        scaled_image = Image(step.image, width=max_width, height=scaled_height)
        story_flow.append(scaled_image)

        # Add space before the next step
        story_flow.append(Spacer(1, 1 * inch))

    # Build the PDF
    pdf.build(story_flow)

    print(Fore.BLUE + f"Story saved to {output_file}")
