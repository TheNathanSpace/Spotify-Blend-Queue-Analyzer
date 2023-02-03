import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes


def graph_blend_trials(ax: Axes, queue: list, title: str):
    ax.set_xlabel("Queue Position")
    ax.set_ylabel("Song #")
    for trial in queue:
        ax.plot(trial)
    ax.set_xticks([i for i in range(0, len(queue))])
    ax.set_xticklabels([i for i in range(1, len(queue) + 1)])
    ax.set_title(title)


if __name__ == '__main__':
    plt.style.use("fast")
    fig, ax = plt.subplots(3)

    queue_1 = json.loads((Path().cwd() / "queue_1.json").read_text())["trials_indices"]
    graph_blend_trials(ax[0], queue_1, "Blend Playlist #1")

    queue_2 = json.loads((Path().cwd() / "queue_2.json").read_text())["trials_indices"]
    graph_blend_trials(ax[1], queue_2, "Blend Playlist #2")

    top_100_queue = json.loads((Path().cwd() / "output_top100.json").read_text())["trials_indices"]
    graph_blend_trials(ax[2], top_100_queue, "Normal Playlist")

    fig.set_figheight(8)
    fig.set_figwidth(9)
    fig.subplots_adjust(hspace = .7)
    fig.suptitle("Queue Progression for Spotify Blend vs. Normal Playlist")
    fig.savefig(fname = "comparison.png")

    fig, ax = plt.subplots(nrows = 4, ncols = 5)

    for i, plot in enumerate(ax.reshape(-1)):
        plot.set_xlabel("Queue Position")
        plot.set_ylabel("Song #")
        plot.plot(queue_2[i])
        plot.set_xticks([i for i in range(0, 21)])
        plot.set_xticklabels([i for i in range(1, 22)])
        plot.set_title(f"Trial {i}")

    fig.set_figheight(12)
    fig.set_figwidth(40)
    fig.subplots_adjust(hspace = .7)
    fig.suptitle("Queue Progression for Spotify Blend Playlist")
    fig.savefig(fname = "all_trials.png", bbox_inches = 'tight', pad_inches = .5)
