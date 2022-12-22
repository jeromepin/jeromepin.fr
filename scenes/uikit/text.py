from typing import List, Union

from manim import (
    VMobject,
)

from .card import Card


class ColoredTextContainer(Card):
    def __init__(
        self,
        color: Union[str, List[str]],
        content: VMobject,
        horizontal_padding: float = 0.2,
        vertical_padding: float = 0.1,
    ):
        super().__init__(
            background_color=color,
            border_width=0,
            border_color=None,
            boder_radius=0.01,
            content=content,
            min_height=content.height + vertical_padding,
            min_width=content.width + horizontal_padding,
            title=None,
        )
