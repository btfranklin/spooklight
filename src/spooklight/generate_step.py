import requests
from openai import OpenAI


def generate_step(llm_client, story, step):
    """
    Generate the next image and narrative for the current step.
    """

    client = OpenAI()

    image_url = generate(client, story)
    download_file(image_url, f"output/{step}.png")

    # Placeholder for image and narrative generation
    return f"output/{step}.png", f"Generated narrative for step {step}"


def download_file(url, local_filename):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Open a local file in binary write mode
        with open(local_filename, "wb") as file:
            # Write the content of the response to the file
            file.write(response.content)
        print(f"File downloaded and saved as {local_filename}")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
