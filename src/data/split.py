import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def split(
    df, cmpframe=0, distfactor=1.5, show=False, add_start=False, add_end=False
):
    if cmpframe == -1:
        start = df[-2:-1]
    else:
        start = df[cmpframe : cmpframe + 1]
    d = dist(start, df).sum(axis=1)
    valleys = find_splits(d, distfactor)
    if add_start:
        valleys = np.append([0], valleys)
    if add_end:
        valleys = np.append(valleys, [len(df) - 1])
    if show:
        plt.figure(figsize=(10, 4))
        plt.plot(d)
        for v in valleys:
            plt.axvline(v, c="red")
        plt.show()
    return [df[a:b] for a, b in zip(valleys[:-1], valleys[1:])]


def signal_of_split(
    df, cmpframe=0, distfactor=1.5, show=False, add_start=False, add_end=False
):
    if cmpframe == -1:
        start = df[-2:-1]
    else:
        start = df[cmpframe : cmpframe + 1]
    d = dist(start, df).sum(axis=1)
    valleys = find_splits(d, distfactor)
    if add_start:
        valleys = np.append([0], valleys)
    if add_end:
        valleys = np.append(valleys, [len(df) - 1])
    return d, valleys


def dist(start, df):
    diffdf = pd.DataFrame()
    for c in df.columns:
        diffdf[c] = (df[c] - start[c].values) ** 2
    return diffdf


def get_frequency(signal):
    ft = np.fft.fft(signal)
    ftabs = np.abs(ft)
    ftabs[0] = 0
    return np.argmax(ftabs[1:20])


def find_splits(signal, distfactor=1.5):
    splitsnb_estimate = get_frequency(signal)
    # print(splitsnb_estimate)
    mph = np.mean(-signal)
    mpd = len(signal) / (distfactor * splitsnb_estimate)
    valleys = _detect_peaks(signal, mpd=mpd, mph=mph, valley=True)
    return valleys


def _detect_peaks(
    x,
    mph=None,
    mpd=1,
    threshold=0,
    edge="rising",
    kpsh=False,
    valley=False,
    show=False,
    ax=None,
):

    """Detect peaks in data based on their amplitude and other features.
    Parameters
    ----------
    x : 1D array_like
        data.
    mph : {None, number}, optional (default = None)
        detect peaks that are greater than minimum peak height.
    mpd : positive integer, optional (default = 1)
        detect peaks that are at least separated 
        by minimum peak distance (in
        number of data).
    valley : bool, optional (default = False)
        if True (1), detect valleys (local minima) instead of peaks.
    show : bool, optional (default = False)
        if True (1), plot data in matplotlib figure.
    ax : a matplotlib.axes.Axes instance, optional (default = None).
    Returns
    -------
    ind : 1D array_like
        indeces of the peaks in `x`.
    Notes
    -----
    The detection of valleys instead of peaks
     is performed internally by simply
    negating the data: `ind_valleys = detect_peaks(-x)`
    """

    x = np.atleast_1d(x).astype("float64")
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
    # find indices of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ["rising", "both"]:
            ire = np.where(
                (np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0)
            )[0]
        if edge.lower() in ["falling", "both"]:
            ife = np.where(
                (np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0)
            )[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[
            np.in1d(
                ind,
                np.unique(np.hstack((indnan, indnan - 1, indnan + 1))),
                invert=True,
            )
        ]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size - 1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(
            np.vstack([x[ind] - x[ind - 1], x[ind] - x[ind + 1]]), axis=0
        )
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) & (
                    x[ind[i]] > x[ind] if kpsh else True
                )
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indices by their occurrence
        ind = np.sort(ind[~idel])

    return ind
