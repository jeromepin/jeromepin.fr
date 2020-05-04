#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import random


def generate_y(const, var):
    return const + random.randint(0, var) / 10


def create_stacked_chart(
    timeframe_length, mischievous_node, color, mischievous_node_first=True
):
    series = [
        [generate_y(10, i) for i in range(int(timeframe_length))],
        [generate_y(10, i) for i in range(int(timeframe_length))],
        [generate_y(10, i) for i in range(int(timeframe_length))],
    ]

    colors = [color + [0.4], color + [0.6], color + [0.8]]

    if mischievous_node_first:
        series = [mischievous_node] + series
        colors = [color + [1]] + list(colors)
        filename = "mischievous_node_first.svg"
    else:
        series = series + [mischievous_node]
        colors = list(colors) + [color + [1]]
        filename = "mischievous_node_last.svg"

    plt.figure(figsize=(15, 4))
    plt.xticks([])
    plt.margins(x=0)
    plt.xlabel("Time (s)", size=12)
    plt.ylabel("Requests", size=12)
    plt.stackplot(range(timeframe_length), series, colors=colors)
    plt.savefig(
        filename, format="svg", dpi=120, transparent=True, bbox_inches="tight"
    )


def create_chart_with_total(timeframe_length, mischievous_node, color):
    series = [
        [generate_y(10, i) for i in range(int(timeframe_length))],
        [generate_y(10, i) for i in range(int(timeframe_length))],
        [generate_y(10, i) for i in range(int(timeframe_length))],
        mischievous_node,
    ]
    colors = [color + [0.4], color + [0.6], color + [0.8], color + [1]]

    plt.figure(figsize=(15, 4))
    plt.xticks([])
    plt.margins(x=0)
    plt.xlabel("Time (s)", size=12)
    plt.ylabel("Requests", size=12)

    for i in range(len(series)):
        plt.plot(range(timeframe_length), series[i], color=colors[i])

    plt.plot(
        range(timeframe_length), [sum(x) for x in zip(*series)], color="black"
    )

    plt.savefig(
        "unstacked.svg",
        format="svg",
        dpi=120,
        transparent=True,
        bbox_inches="tight",
    )


timeframe_length = 100
mischievous_node = (
    [generate_y(30, i) for i in range(int(timeframe_length / 2))]
    + [11, 10, 10, 8]
    + [generate_y(30, i) for i in range(int(timeframe_length / 2) - 4)]
)
color = [0.95, 0.501, 0.215]

create_stacked_chart(timeframe_length, mischievous_node, color)
create_stacked_chart(
    timeframe_length, mischievous_node, color, mischievous_node_first=False
)
create_chart_with_total(timeframe_length, mischievous_node, color)
