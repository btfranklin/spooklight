import os
from colorama import Back, Fore
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
from reportlab.lib.units import inch
from PIL import Image as PILImage

from spooklight.settings import Settings


def build_pdf_from_story_files() -> None:
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

    # Add a title page with the story concept (Concept)
    title_file = os.path.join(output_dir, "title.txt")
    concept_file = os.path.join(output_dir, "concept.txt")

    if os.path.exists(title_file):
        with open(title_file, "r") as f:
            title = f.read().strip()
        title_style = styles["Title"]
        story_flow.append(Paragraph(title, title_style))
        story_flow.append(Spacer(1, 0.5 * inch))  # Adds some space after the title
    else:
        print(Fore.RED + f"Warning: Title file '{title_file}' not found.")

    if os.path.exists(concept_file):
        with open(concept_file, "r") as f:
            concept = f.read().strip()
        concept_heading = Paragraph("<b>Concept</b>", styles["Heading2"])
        concept_text = Paragraph(concept, styles["BodyText"])
        story_flow.append(concept_heading)
        story_flow.append(Spacer(1, 0.2 * inch))  # Space after the heading
        story_flow.append(concept_text)
        story_flow.append(PageBreak())  # Start a new page after the concept
    else:
        print(Fore.RED + f"Warning: Concept file '{concept_file}' not found.")

    # Add each step to the PDF
    step = 0
    while True:
        narrative_file = os.path.join(output_dir, f"{step}.txt")
        image_file = os.path.join(output_dir, f"{step}.png")

        if not os.path.exists(narrative_file) or not os.path.exists(image_file):
            break

        # Adjust the image size to fit within a max height of 4.5 inches, maintaining aspect ratio
        with PILImage.open(image_file) as img:
            img_width, img_height = img.size
            max_height = 4.5 * inch
            aspect_ratio = img_width / img_height

            if img_height > max_height:
                img_height = max_height
                img_width = max_height * aspect_ratio

            # Ensure the image does not exceed the page width
            max_width = 6.5 * inch  # Adjusting for margins
            if img_width > max_width:
                img_width = max_width
                img_height = max_width / aspect_ratio

        # Add image to the PDF
        story_flow.append(Image(image_file, width=img_width, height=img_height))
        story_flow.append(Spacer(1, 0.5 * inch))  # Space between image and narrative

        # Add narrative with paragraph separation
        with open(narrative_file, "r") as f:
            narrative = f.read().strip()

        # Split the narrative into paragraphs based on double newlines
        paragraphs = narrative.split("\n\n")
        for paragraph in paragraphs:
            story_flow.append(Paragraph(paragraph.strip(), styles["BodyText"]))
            story_flow.append(Spacer(1, 0.2 * inch))  # Space between paragraphs

        story_flow.append(PageBreak())  # Start a new page for the next step

        step += 1

    # Build the PDF
    pdf.build(story_flow)

    print(Fore.BLUE + f"Story saved to {output_file}")
