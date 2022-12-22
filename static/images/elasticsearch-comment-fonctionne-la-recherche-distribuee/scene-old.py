from manim import *
import manimpango
from typing import Any, Dict, List, Optional

BACKGROUND_COLOR = "#141414"
GREEN_TO_BLUE_RADIENT = ["#51aeec", "#88e4a8"]
RED_TO_PINK_RADIENT = ["#fb59a5", "#fa1e1e"]
BLUE_TO_PINK_RADIENT = ["#fb59a5", "#51aeec"]
DEFAULT_FONT_FAMILY = "Noto Sans"  # "sans-serif"

config.background_color = BACKGROUND_COLOR


class JRoundedRectangle(RoundedRectangle):
    def __init__(self, fill_color):
        super().__init__()
        self.corner_radius = (0.01,)
        self.fill_color = fill_color
        self.fill_opacity = (1,)
        self.stroke_color = (None,)
        self.stroke_opacity = (0,)
        self.stroke_width = (0,)


class ColoredTextContainer(VGroup):
    def __init__(
        self,
        color: typing.Union[str, List[str]],
        content: VMobject,
        horizontal_margin: float = 0.2,
        vertical_margin: float = 0.1,
    ):
        super().__init__()
        container = RoundedRectangle(
            corner_radius=0.01,
            fill_color=color,
            fill_opacity=1,
            stroke_color=None,
            stroke_opacity=0,
            stroke_width=0,
            width=content.width + horizontal_margin,
            height=content.height + vertical_margin,
        )

        self.add(container)
        container.add(content)


class StepCard(VGroup):
    # TODO: Add margins for step_rectangle
    def __init__(
        self,
        step: int,
        description: List[str],
        card_color: typing.Union[str, List[str]],
        step_color: typing.Union[str, List[str]],
        description_t2g=None,
        description_t2w=None,
    ):
        super().__init__()

        card = RoundedRectangle(
            corner_radius=0.01,
            fill_color=card_color,
            fill_opacity=1,
            stroke_color=None,
            stroke_opacity=0,
            stroke_width=0,
            width=2,
            height=1.2,
        )
        self.add(card)

        step_rectangle = ColoredTextContainer(
            color=step_color,
            content=Text(f"Step {step}", font_size=12, font=DEFAULT_FONT_FAMILY),
        )
        card.add(step_rectangle)

        step_rectangle.align_to(card, LEFT).align_to(card, UP)

        description_text = Paragraph(
            *description,
            font_size=12,
            font=DEFAULT_FONT_FAMILY,
            t2g=description_t2g,
            t2w=description_t2w,
        )
        card.add(description_text)


class RectangleWithTitle(VGroup):
    def __init__(
        self,
        title: str,
        color: typing.Union[str, List[str]],
        content: Optional[VMobject] = None,
        width: float = 1.5,
        height: float = 1,
    ):
        super().__init__()
        self.content_container = RoundedRectangle(
            corner_radius=0.01,
            stroke_color=color,
            width=width,
            height=height,
        )
        self.add(self.content_container)

        self.title_text = MarkupText(title, font_size=16, font=DEFAULT_FONT_FAMILY)

        self.title_container = RoundedRectangle(
            corner_radius=0.01,
            stroke_color=color,
            fill_color=BACKGROUND_COLOR,
            fill_opacity=1,
            width=self.title_text.width + 0.5,
            height=self.title_text.height + 0.2,
        )
        self.add(self.title_container)

        self.title_container.add(self.title_text)

        self.title_container.move_to(self.content_container.get_edge_center(UP))

        if content is not None:
            self.content = content
            self.add(self.content)


class Steps(VGroup):
    def __init__(self, contents: List[List[str]], highlights: Dict[str, Any]):
        super().__init__()

        self.current_step = -1
        index = 0

        t2w = {highlight: "BOLD" for highlight in list(highlights.keys())}

        for content in contents:
            index += 1
            step = StepCard(
                step=index,
                description=content,
                description_t2g=highlights,
                description_t2w=t2w,
                card_color="#282828",
                step_color="#FF9301",
            )
            self.add(step)

        self.set_opacity(0.1)

    def next(self):
        self.submobjects[self.current_step].set_opacity(0.1)
        self.current_step += 1
        self.submobjects[self.current_step].set_opacity(1)


# self.add(....) : show
# self.play(Write(...)) : draw
# NOTE: Everything MUST fit into the scene. The viewport will not change its size to accomodate objects inside it.

# TODO: implement a step (in the meaning of a Keynote slide equivalent) as a first class object in a JScene class
# TODO: save the state of all objects at the end of every step
# TODO: implement ? a StateManager to easily restore the state of a given object from a given step


class QueryPhase(Scene):
    def _generate_shards_vgroup(self, green: str, pink: str, font_size: int = 12):
        vmobjects = []

        vmobjects.append(
            ColoredTextContainer(
                GREEN,
                MarkupText(green, font_size=font_size, font=DEFAULT_FONT_FAMILY),
            )
        )

        if pink:
            vmobjects.append(
                ColoredTextContainer(
                    PINK,
                    MarkupText(pink, font_size=font_size, font=DEFAULT_FONT_FAMILY),
                )
            )

        return VGroup(*vmobjects).arrange(direction=DOWN, buff=0.1)

    def construct(self):
        self.DEFAULT_WAIT_DURATION = 1
        steps = Steps(
            contents=[
                ["The client requests", "one of the cluster's", "node"],
                ["The node became a", "coordinating node"],
                [
                    "The coordinating node",
                    "broadcast the request",
                    "to every shard in the",
                    "index",
                ],
                [
                    "Every shard creates",
                    "a sorted priority queue",
                    "containing documents",
                    "IDs",
                ],
                ["Shards return their", "priority queue to", "the coordinating node"],
                ["The coordinating node", "merges the queues", "and sorts it"],
            ],
            highlights={
                "coordinating node": BLUE_TO_PINK_RADIENT,
                "priority queue": RED_TO_PINK_RADIENT,
            },
        )

        self.add(steps.arrange(direction=RIGHT).move_to(UP * 3))

        #####################################################
        #                      STEP 1
        #####################################################
        steps.next()

        client = RectangleWithTitle(title="Client", color=RED_TO_PINK_RADIENT).move_to(
            LEFT * 5
        )
        node1 = RectangleWithTitle(
            title="Node 1",
            color=GREEN_TO_BLUE_RADIENT,
            content=self._generate_shards_vgroup("P", "R"),
        ).move_to(RIGHT * 5)

        node0 = RectangleWithTitle(
            title="Node 0",
            color=GREEN_TO_BLUE_RADIENT,
            content=self._generate_shards_vgroup("R", "R"),
        ).next_to(node1, UP)

        node2 = RectangleWithTitle(
            title="Node 2",
            color=GREEN_TO_BLUE_RADIENT,
            content=self._generate_shards_vgroup("R", "P"),
        ).next_to(node1, DOWN)

        node2.save_state()

        self.add(client, node1, node0, node2)

        self.wait(self.DEFAULT_WAIT_DURATION)

        client_to_node0 = Arrow(
            start=client.get_edge_center(RIGHT),
            end=node0.get_edge_center(LEFT),
            stroke_width=3,
        )

        self.play(Create(client_to_node0))

        #####################################################
        #                      STEP 2
        #####################################################
        steps.next()

        coordinating_node = RectangleWithTitle(
            title="Coordinating Node",
            color=BLUE_TO_PINK_RADIENT,
            content=self._generate_shards_vgroup("R", "R"),
        ).next_to(node1, UP)

        self.play(Transform(node0, coordinating_node), FadeOut(client_to_node0))

        self.wait(self.DEFAULT_WAIT_DURATION)

        #####################################################
        #                      STEP 3
        #####################################################
        steps.next()

        coordinating_node_to_node_1 = CurvedArrow(
            start_point=coordinating_node.title_container.get_edge_center(RIGHT),
            end_point=node1.title_container.get_edge_center(RIGHT),
            stroke_width=2,
            angle=-(TAU / 4),
        )

        coordinating_node_to_node_2 = CurvedArrow(
            start_point=coordinating_node.title_container.get_edge_center(RIGHT),
            end_point=node2.title_container.get_edge_center(RIGHT),
            stroke_width=2,
            angle=-(TAU / 4),
        )

        self.play(
            Create(coordinating_node_to_node_1), Create(coordinating_node_to_node_2)
        )

        self.wait(self.DEFAULT_WAIT_DURATION)

        #####################################################
        #                      STEP 4
        #####################################################
        steps.next()

        self.play(
            FadeOut(
                client,
                coordinating_node,
                node0,
                node1,
                coordinating_node_to_node_1,
                coordinating_node_to_node_2,
            )
        )

        big_node2 = RectangleWithTitle(
            title="Node 2",
            color=GREEN_TO_BLUE_RADIENT,
            content=self._generate_shards_vgroup(green="R", pink=None, font_size=24),
            height=3,
            width=2,
        )

        self.play(Transform(node2, big_node2))

        big_node2_to_shard_arrow = Arrow(
            start=big_node2.title_container.get_edge_center(DOWN),
            end=big_node2.content.get_edge_center(UP),
        )

        shard_to_big_node2_arrow = Arrow(
            start=big_node2.content.get_edge_center(UP),
            end=big_node2.title_container.get_edge_center(DOWN),
        )

        priority_queue = (
            VGroup(
                ColoredTextContainer(
                    color=RED_TO_PINK_RADIENT,
                    content=Text("49", font_size=12, font=DEFAULT_FONT_FAMILY),
                ),
                ColoredTextContainer(
                    color=RED_TO_PINK_RADIENT,
                    content=Text("12", font_size=12, font=DEFAULT_FONT_FAMILY),
                ),
                ColoredTextContainer(
                    color=RED_TO_PINK_RADIENT,
                    content=Text("86", font_size=12, font=DEFAULT_FONT_FAMILY),
                ),
            )
            .arrange(direction=DOWN, buff=0)
            .next_to(shard_to_big_node2_arrow, RIGHT)
        )

        self.add(big_node2_to_shard_arrow, shard_to_big_node2_arrow, priority_queue)

        self.wait(self.DEFAULT_WAIT_DURATION)

        #####################################################
        #                      STEP 5
        #####################################################
        steps.next()

        self.play(
            FadeOut(big_node2_to_shard_arrow, shard_to_big_node2_arrow, priority_queue)
        )

        self.play(
            FadeIn(
                client,
                coordinating_node,
                node0,
                node1,
            ),
            Restore(node2),
        )

        node_1_to_coordinating_node = CurvedArrow(
            start_point=node1.title_container.get_edge_center(RIGHT),
            end_point=coordinating_node.title_container.get_edge_center(RIGHT),
            stroke_width=2,
            angle=(TAU / 4),
        )

        node_2_to_coordinating_node = CurvedArrow(
            start_point=node2.title_container.get_edge_center(RIGHT),
            end_point=coordinating_node.title_container.get_edge_center(RIGHT),
            stroke_width=2,
            angle=(TAU / 4),
        )

        self.play(
            Create(node_1_to_coordinating_node), Create(node_2_to_coordinating_node)
        )

        self.wait(self.DEFAULT_WAIT_DURATION)
        #####################################################
        #                      STEP 6
        #####################################################
        steps.next()

        self.wait(self.DEFAULT_WAIT_DURATION * 2)
