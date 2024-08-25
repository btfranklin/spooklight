import os
from colorama import Back, Fore
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.units import inch

from spooklight.model import Story
from spooklight.settings import Settings


def build_pdf_from_story_files(
    llm_client: OpenAI,
    story: Story,
) -> None:
    """
    Generate a PDF from the text and image files in the output directory.
    """

    print(Back.BLUE + "BUILDING PDF FROM STORY FILES")

    output_dir = Settings.get_output_directory()
    output_file = os.path.join(output_dir, "story.pdf")

    # Create a PDF document
    pdf = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story_flow = []

    # Add a title page
    title_file = os.path.join(output_dir, "title.txt")
    if os.path.exists(title_file):
        with open(title_file, "r") as f:
            title = f.read().strip()
        title_style = styles["Title"]
        story_flow.append(Paragraph(title, title_style))
        story_flow.append(Spacer(1, 2 * inch))  # Adds some space after the title
    else:
        print(Fore.RED + f"Warning: Title file '{title_file}' not found.")

    # Add each step to the PDF
    step = 0
    while True:
        narrative_file = os.path.join(output_dir, f"{step}.txt")
        image_file = os.path.join(output_dir, f"{step}.png")

        if not os.path.exists(narrative_file) or not os.path.exists(image_file):
            break

        # Add narrative
        with open(narrative_file, "r") as f:
            narrative = f.read().strip()
        story_flow.append(Paragraph(narrative, styles["BodyText"]))
        story_flow.append(Spacer(1, 0.5 * inch))  # Space between narrative and image

        # Add image
        story_flow.append(Image(image_file, width=6 * inch, height=4.5 * inch))
        story_flow.append(Spacer(1, 1 * inch))  # Space before the next step

        step += 1

    # Build the PDF
    pdf.build(story_flow)

    print(Back.BLUE + f"Story saved to {output_file}")
