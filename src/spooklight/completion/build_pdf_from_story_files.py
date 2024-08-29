import os
from colorama import Back, Fore
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageBreak
from reportlab.lib.units import inch

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

        # Add image
        story_flow.append(Image(image_file, width=6 * inch, height=4.5 * inch))
        story_flow.append(Spacer(1, 0.5 * inch))  # Space between image and narrative

        # Add narrative
        with open(narrative_file, "r") as f:
            narrative = f.read().strip()
        story_flow.append(Paragraph(narrative, styles["BodyText"]))
        story_flow.append(PageBreak())  # Start a new page for the next step

        step += 1

    # Build the PDF
    pdf.build(story_flow)

    print(Fore.BLUE + f"Story saved to {output_file}")
