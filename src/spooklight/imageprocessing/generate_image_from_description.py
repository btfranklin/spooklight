import requests
from spooklight.settings import Settings


def generate_image_from_description(llm_client, image_description):

    response = llm_client.images.generate(
        model=Settings.get_generate_image_model(),
        prompt=image_description,
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
        print(f"Image downloaded into memory from {image_url}")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")

    return image
