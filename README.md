# spooklight

Spooklight is an image-driven generative storytelling tool. It uses a multimodal LLM to generate narratives driven by descriptions of images, and to generate images from narratives. These activities alternate in a cycle, extending the story and adding new images to the narrative.

The name "spooklight" refers to an American folk name for the will-o-the-wisp, a mystical being that leads people deep into mysterious places.

## Methodology

The primary methodology of the project is to use a multimodal LLM to observe and describe images, using those observations as the guiding "ground truths" for the LLM to generate narratives and images. This injection of an externalized stochastic process into the LLM allows for a richer and more diverse generation of text, while simultaneously providing a rich set of images that enhance the story.

## Configuration Parameters

The tool has various parameters that can be provided at execution time, which control the nature of the generation process. These parameters are:

- `--starting-image-path`: A string that specifies the path to the image that will be used as the starting point for the story.
- `--starting-image-description`: A string that will be used as the prompt for the LLM to generate the first image in the story. This image will be used as the starting point for the story. This will be ignored if the `starting-image-path` parameter is provided.
- `--story-concept`: REQUIRED. A string that provides a summary of the story concept. This will be used throughout the story at every step to provide context and guide the LLM.
- `--story-length`: An integer that specifies the length of the story in terms of number of steps. Each "step" is a single image and associated narrative.

If neither the `starting-image-path` nor the `starting-image-description` parameter are provided, the tool will use the story concept to generate an image description, and then use that description to generate the first image in the story.

If the `story-length` parameter is not provided, the story will simply continue until it reaches a natural conclusion, or until the user terminates the tool manually.

Please note that the only required parameter is the `story-concept` parameter.

## License

Spooklight is released under the [MIT License](LICENSE).