class Settings:

    # Read/Write settings
    __story_length: int | None = None

    # Read-only settings
    __output_directory: str = "output"
    __generate_story_concept_from_image_description_model: str = "gpt-4o"
    __enhance_story_concept_model: str = "gpt-4o"
    __describe_image_model: str = "gpt-4o"
    __generate_image_description_model: str = "gpt-4o"
    __generate_visual_style_model: str = "gpt-4o"
    __generate_image_model: str = "dall-e-3"
    __generate_narrative_model: str = "gpt-4o"
    __generate_title_model: str = "gpt-4o"

    # Read/Write Accessors
    @classmethod
    def set_story_length(cls, number: int):
        cls.__story_length = number

    @classmethod
    def get_story_length(cls) -> int:
        return cls.__story_length

    # Read-only Accessors
    @classmethod
    def get_output_directory(cls) -> str:
        return cls.__output_directory

    @classmethod
    def get_generate_story_concept_from_image_description_model(cls) -> str:
        return cls.__generate_story_concept_from_image_description_model

    @classmethod
    def get_enhance_story_concept_model(cls) -> str:
        return cls.__enhance_story_concept_model

    @classmethod
    def get_describe_image_model(cls) -> str:
        return cls.__describe_image_model

    @classmethod
    def get_generate_image_description_model(cls) -> str:
        return cls.__generate_image_description_model

    @classmethod
    def get_generate_visual_style_model(cls) -> str:
        return cls.__generate_visual_style_model

    @classmethod
    def get_generate_image_model(cls) -> str:
        return cls.__generate_image_model

    @classmethod
    def get_generate_narrative_model(cls) -> str:
        return cls.__generate_narrative_model

    @classmethod
    def get_generate_title_model(cls) -> str:
        return cls.__generate_title_model
