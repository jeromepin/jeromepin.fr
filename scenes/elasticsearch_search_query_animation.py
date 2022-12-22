from typing import Any, Dict, List, Optional

from manim import *
import manimpango

from uikit.colors import *
from uikit.card import Card
from uikit.rectangle import RectangleWithTitle
from uikit.text import ColoredTextContainer

BACKGROUND_COLOR = "#141414"
DEFAULT_FONT_FAMILY = DEFAULT_FONT  # "Noto Sans"  # "sans-serif"

config.background_color = BACKGROUND_COLOR


class StepCard(Card):
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
        super().__init__(
            background_color=card_color,
        )

        step_number = ColoredTextContainer(
            color=step_color,
            content=Text(f"Step {step}", font_size=12, font=DEFAULT_FONT_FAMILY),
        )

        step_description = Paragraph(
            *description,
            font_size=10,
            font=DEFAULT_FONT_FAMILY,
            t2g=description_t2g,
            t2w=description_t2w,
            disable_ligatures=True,
        )

        step_number.align_to(self, UP).align_to(self, LEFT)

        self.add(step_number, step_description)


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


# TODO: implement a step (in the meaning of a Keynote slide equivalent) as a first class object in a JScene class
# TODO: save the state of all objects at the end of every step
# TODO: implement ? a StateManager to easily restore the state of a given object from a given step


class QueryPhase(Scene):
    def _generate_shards_vgroup(self, green: str, pink: str, font_size: int = 12):
        vmobjects = []

        vmobjects.append(
            ColoredTextContainer(
                color=GREEN,
                content=MarkupText(
                    green, font_size=font_size, font=DEFAULT_FONT_FAMILY
                ),
            )
        )

        if pink:
            vmobjects.append(
                ColoredTextContainer(
                    color=PINK,
                    content=MarkupText(
                        pink, font_size=font_size, font=DEFAULT_FONT_FAMILY
                    ),
                )
            )

        return VGroup(*vmobjects).arrange(direction=DOWN, buff=0.1)

    def construct(self):
        self.DEFAULT_WAIT_DURATION = 1
        steps = Steps(
            # contents=[["foo"] for _ in range(1, 7)],
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

        client = RectangleWithTitle(
            background_color=BACKGROUND_COLOR,
            title="Client",
            border_color=RED_TO_PINK_RADIENT,
            border_width=3,
        ).move_to(LEFT * 5)
        node1 = RectangleWithTitle(
            background_color=BACKGROUND_COLOR,
            title="Node 1",
            border_color=GREEN_TO_BLUE_RADIENT,
            border_width=3,
            content=self._generate_shards_vgroup("P", "R"),
        ).move_to(RIGHT * 5)

        node0 = RectangleWithTitle(
            background_color=BACKGROUND_COLOR,
            title="Node 0",
            border_color=GREEN_TO_BLUE_RADIENT,
            border_width=3,
            content=self._generate_shards_vgroup("R", "R"),
        ).next_to(node1, UP)

        node2 = RectangleWithTitle(
            background_color=BACKGROUND_COLOR,
            title="Node 2",
            border_color=GREEN_TO_BLUE_RADIENT,
            border_width=3,
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
            background_color=BACKGROUND_COLOR,
            title="Coordinating Node",
            border_color=BLUE_TO_PINK_RADIENT,
            border_width=3,
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

        # #####################################################
        # #                      STEP 4
        # #####################################################
        # steps.next()

        # self.play(
        #     FadeOut(
        #         client,
        #         coordinating_node,
        #         node0,
        #         node1,
        #         coordinating_node_to_node_1,
        #         coordinating_node_to_node_2,
        #     )
        # )

        # big_node2 = Card(
        #     background_color=BACKGROUND_COLOR,
        #     title="Node 2",
        #     border_color=GREEN_TO_BLUE_RADIENT,
        #     border_width=3,
        #     content=self._generate_shards_vgroup(green="R", pink=None, font_size=24),
        #     min_height=3,
        #     min_width=2,
        # )

        # self.play(Transform(node2, big_node2))

        # big_node2_to_shard_arrow = Arrow(
        #     start=big_node2.title_container.get_edge_center(DOWN),
        #     end=big_node2.content.get_edge_center(UP),
        # )

        # shard_to_big_node2_arrow = Arrow(
        #     start=big_node2.content.get_edge_center(UP),
        #     end=big_node2.title_container.get_edge_center(DOWN),
        # )

        # priority_queue = (
        #     VGroup(
        #         ColoredTextContainer(
        #             color=RED_TO_PINK_RADIENT,
        #             content=Text("49", font_size=12, font=DEFAULT_FONT_FAMILY),
        #         ),
        #         ColoredTextContainer(
        #             color=RED_TO_PINK_RADIENT,
        #             content=Text("12", font_size=12, font=DEFAULT_FONT_FAMILY),
        #         ),
        #         ColoredTextContainer(
        #             color=RED_TO_PINK_RADIENT,
        #             content=Text("86", font_size=12, font=DEFAULT_FONT_FAMILY),
        #         ),
        #     )
        #     .arrange(direction=DOWN, buff=0)
        #     .next_to(shard_to_big_node2_arrow, RIGHT)
        # )

        # self.add(big_node2_to_shard_arrow, shard_to_big_node2_arrow, priority_queue)

        # self.wait(self.DEFAULT_WAIT_DURATION)

        # #####################################################
        # #                      STEP 5
        # #####################################################
        # steps.next()

        # self.play(
        #     FadeOut(big_node2_to_shard_arrow, shard_to_big_node2_arrow, priority_queue)
        # )

        # self.play(
        #     FadeIn(
        #         client,
        #         coordinating_node,
        #         node0,
        #         node1,
        #     ),
        #     Restore(node2),
        # )

        # node_1_to_coordinating_node = CurvedArrow(
        #     start_point=node1.title_container.get_edge_center(RIGHT),
        #     end_point=coordinating_node.title_container.get_edge_center(RIGHT),
        #     stroke_width=2,
        #     angle=(TAU / 4),
        # )

        # node_2_to_coordinating_node = CurvedArrow(
        #     start_point=node2.title_container.get_edge_center(RIGHT),
        #     end_point=coordinating_node.title_container.get_edge_center(RIGHT),
        #     stroke_width=2,
        #     angle=(TAU / 4),
        # )

        # self.play(
        #     Create(node_1_to_coordinating_node), Create(node_2_to_coordinating_node)
        # )

        # self.wait(self.DEFAULT_WAIT_DURATION)
        # #####################################################
        # #                      STEP 6
        # #####################################################
        # steps.next()

        # self.wait(self.DEFAULT_WAIT_DURATION * 2)
