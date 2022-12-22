from typing import Optional, List, Union

from manim import (
    MarkupText as ManimMarkupText,
    RoundedRectangle as ManimRoundedRectangle,
    UP,
    VGroup,
    VMobject,
)

from .colors import DEFAULT_FONT


class Card(VGroup):
    def __init__(
        self,
        background_color: Union[str, List[str]],
        border_width: Optional[float] = 0,
        border_color: Optional[Union[str, List[str]]] = None,
        boder_radius: float = 0.02,
        content: Optional[VMobject] = None,
        min_height: float = 1,
        min_width: float = 1.5,
        title_size: float = 16,
        title: Optional[str] = None,
    ):
        super().__init__()

        self.background_color = background_color
        self.border_color = border_color
        self.boder_radius = boder_radius

        if content:
            width = content.width if content.width > min_width else min_width
            height = content.height if content.height > min_height else min_height

        else:
            width = min_width
            height = min_height

        self.content_container = ManimRoundedRectangle(
            corner_radius=self.boder_radius,
            fill_color=self.background_color,
            fill_opacity=1,
            stroke_color=self.border_color,
            stroke_opacity=1,
            stroke_width=border_width,
            width=width,
            height=height,
        )

        self.add(self.content_container)

        if title is not None:
            self.title_text = ManimMarkupText(
                title, font_size=title_size, font=DEFAULT_FONT
            )

            self.title_container = ManimRoundedRectangle(
                corner_radius=self.boder_radius,
                fill_color=self.background_color,
                fill_opacity=1,
                stroke_color=self.border_color,
                stroke_opacity=1,
                stroke_width=border_width,
                width=self.title_text.width + 0.5,
                height=self.title_text.height + 0.2,
            )
            self.add(self.title_container)

            self.title_container.add(self.title_text)

            self.title_container.move_to(self.content_container.get_edge_center(UP))

        if content:
            self.content = content
            self.content_container.add(self.content)
