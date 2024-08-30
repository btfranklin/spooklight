from colorama import Back, Fore
import requests
from spooklight.imageprocessing.reencode_image import reencode_image
from spooklight.settings import Settings


def generate_image_from_description(*, llm_client, image_description, visual_style):

    print(Back.MAGENTA + "GENERATING NEXT IMAGE FROM DESCRIPTION")

    prompt = f"{image_description}\n\n{visual_style}"

    print(Fore.BLUE + "Prompt: " + Fore.YELLOW + prompt)

    response = llm_client.images.generate(
        model=Settings.get_generate_image_model(),
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        n=1,
    )

    image_url = response.data[0].url

    # Send a GET request to the URL
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        image = response.content
        print(Fore.BLUE + f"Image downloaded into memory from {image_url}")
    else:
        print(
            Fore.RED
            + f"Failed to download the file. Status code: {response.status_code}"
        )

    # Re-encode the image to PNG format
    print(Fore.BLUE + "Re-encoding image to PNG format")
    image = reencode_image(image, target_format="PNG")

    return image
