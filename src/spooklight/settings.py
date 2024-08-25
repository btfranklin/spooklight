class Settings:

    # Read/Write settings
    __story_length: int | None = None

    # Read-only settings
    __generate_story_concept_from_image_description_model: str = "chatgpt-4o-latest"
    __enhance_story_concept_model: str = "chatgpt-4o-latest"
    __describe_image_model: str = "chatgpt-4o-latest"
    __generate_next_image_description_model: str = "chatgpt-4o-latest"
    __generate_image_model: str = "dall-e-3"
    __generate_next_narrative_model: str = "chatgpt-4o-latest"

    # Read/Write Accessors
    @classmethod
    def set_story_length(cls, number: int):
        cls.__story_length = number

    @classmethod
    def get_story_length(cls) -> int:
        return cls.__story_length

    # Read-only Accessors
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
    def get_generate_next_image_description_model(cls) -> str:
        return cls.__generate_next_image_description_model

    @classmethod
    def get_generate_image_model(cls) -> str:
        return cls.__generate_image_model

    @classmethod
    def get_generate_next_narrative_model(cls) -> str:
        return cls.__generate_next_narrative_model
