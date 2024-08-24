import base64

from promptdown import StructuredPrompt
from typing import Any
from openai import OpenAI
from settings import Settings


def encode_bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def read_image(image_path) -> bytes:
    with open(image_path, "rb") as image_file:
        return image_file.read()


def encode_image_at_path(image_path) -> str:
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        return encoded_image


def describe_image_at_path(llm_client: OpenAI, image_path: str) -> str:

    base64_encoded_image = encode_image_at_path(image_path)

    return describe_encoded_image(llm_client, base64_encoded_image)


def describe_encoded_image(llm_client: OpenAI, base64_encoded_image: bytes) -> str:

    structured_prompt = StructuredPrompt.from_package_resource(
        package="spooklight", resource_name="describe_image.prompt.md"
    )
    messages = structured_prompt.to_chat_completion_messages()

    # Get the last message from the structured prompt
    last_message_content: str | list[dict[str, Any]] = messages[-1]["content"]
    if isinstance(last_message_content, list):
        last_message_content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_encoded_image}"},
            }
        )
        messages[-1]["content"] = last_message_content

    response = llm_client.chat.completions.create(
        model=Settings.get_describe_image_model(),
        messages=messages,
        temperature=1,
        max_tokens=4096,
    )

    return response.choices[0].message.content
