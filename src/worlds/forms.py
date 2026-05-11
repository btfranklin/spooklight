from __future__ import annotations

from django import forms

from worlds.models import World


FIELD_CLASS = (
    "w-full rounded-lg border border-base-300 bg-base-100 px-4 py-3 "
    "text-base-content outline-none transition focus:border-primary"
)


class WorldForm(forms.ModelForm):
    class Meta:
        model = World
        fields = ["name", "description", "genre", "aesthetic_notes"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Riverpunk kingdoms, salt moon colony...",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": FIELD_CLASS,
                    "rows": 4,
                    "placeholder": "A short seed for what makes this world distinct.",
                }
            ),
            "genre": forms.TextInput(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": (
                        "Cosmic horror, riverpunk, mythic science fantasy..."
                    ),
                }
            ),
            "aesthetic_notes": forms.Textarea(
                attrs={
                    "class": FIELD_CLASS,
                    "rows": 5,
                    "placeholder": (
                        "Visual texture, tone, recurring motifs, materials, "
                        "lighting, period references..."
                    ),
                }
            ),
        }
