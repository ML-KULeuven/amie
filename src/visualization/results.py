import matplotlib.pyplot as plt
import numpy as np


def errorbars(scores, figsize=(3, 2), show=True):
    keys = list(scores.keys())
    errmeans = [1 - np.mean(x) for x in scores.values()]
    errstds = [np.std(x) for x in scores.values()]
    y_pos = range(len(keys))
    plt.figure(figsize=figsize)
    plt.barh(y_pos, errmeans, xerr=errstds)
    plt.gca().set_yticks(y_pos)
    plt.gca().set_yticklabels(keys)
    plt.xlabel("Prediction error")
    # plt.xlim(0,0.5)
    plt.tight_layout()
    if show:
        plt.show()
