from __future__ import annotations

from django import forms

from worlds.forms import FIELD_CLASS
from worlds.models import World
from world_artifacts.models import (
    ImportantEvent,
    StoryConcept,
    WorldCharacter,
    WorldImageReference,
    WorldLocation,
    WorldTruth,
)


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", FIELD_CLASS)
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 4)


class WorldAestheticsForm(StyledModelForm):
    class Meta:
        model = World
        fields = ["genre", "aesthetic_notes"]
        widgets = {
            "genre": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "aesthetic_notes": forms.Textarea(
                attrs={"class": FIELD_CLASS, "rows": 7}
            ),
        }


class WorldTruthForm(StyledModelForm):
    class Meta:
        model = WorldTruth
        fields = ["title", "text", "notes"]


class WorldCharacterForm(StyledModelForm):
    class Meta:
        model = WorldCharacter
        fields = [
            "title",
            "role",
            "appearance",
            "personality",
            "motivations",
            "current_status",
            "notes",
        ]


class WorldLocationForm(StyledModelForm):
    class Meta:
        model = WorldLocation
        fields = [
            "title",
            "location_type",
            "geography",
            "visual_character",
            "significance",
            "notes",
        ]


class ImportantEventForm(StyledModelForm):
    class Meta:
        model = ImportantEvent
        fields = [
            "title",
            "time_period",
            "event_state",
            "participants",
            "causes",
            "consequences",
            "notes",
        ]


class WorldImageReferenceForm(StyledModelForm):
    class Meta:
        model = WorldImageReference
        fields = ["title", "image", "source", "role", "description", "notes"]


class StoryConceptForm(StyledModelForm):
    class Meta:
        model = StoryConcept
        fields = ["title", "seed", "premise", "notes"]
