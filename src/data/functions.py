import numpy as np
import pandas as pd
import json
import array
from sklearn.decomposition import PCA
import os

width = 512
height = 424


def getbones(body):
    joints = body["Joints"]

    def bone(a, b):
        return joints[a], joints[b]

    bones = [
        # torso
        bone("Head", "Neck"),
        bone("Neck", "SpineShoulder"),
        bone("SpineShoulder", "SpineMid"),
        bone("SpineMid", "SpineBase"),
        bone("SpineShoulder", "ShoulderRight"),
        bone("SpineShoulder", "ShoulderLeft"),
        bone("SpineBase", "HipRight"),
        bone("SpineBase", "HipLeft"),
        # Right Arm
        bone("ShoulderRight", "ElbowRight"),
        bone("ElbowRight", "WristRight"),
        bone("WristRight", "HandRight"),
        bone("HandRight", "HandTipRight"),
        bone("WristRight", "ThumbRight"),
        # Left Arm
        bone("ShoulderLeft", "ElbowLeft"),
        bone("ElbowLeft", "WristLeft"),
        bone("WristLeft", "HandLeft"),
        bone("HandLeft", "HandTipLeft"),
        bone("WristLeft", "ThumbLeft"),
        # Right Leg
        bone("HipRight", "KneeRight"),
        bone("KneeRight", "AnkleRight"),
        bone("AnkleRight", "FootRight"),
        # Left Leg
        bone("HipLeft", "KneeLeft"),
        bone("KneeLeft", "AnkleLeft"),
        bone("AnkleLeft", "FootLeft"),
    ]
    return bones


def bonecoordinates(bone):
    a, b = bone[0]["Position"], bone[1]["Position"]
    x = [a["X"], b["X"]]
    y = [a["Y"], b["Y"]]
    z = [a["Z"], b["Z"]]
    return x, y, z


def getbodydepth(depth, bodyindex, frame=None):
    if not frame:
        a = depth[frame, :, :]
        b = bodyindex[frame, :, :]
        return a * (b < 10)
    else:
        return [a * (b < 10) for a, b in zip(depth, bodyindex)]


def bodydepth_to_pointcloud(bodydepth, perc=0.1):
    x, y = np.meshgrid(range(0, width), range(0, height))
    z = bodydepth.copy()
    x, y, z = x.flatten(), y.flatten(), z.flatten()

    indices = range(0, width * height, int(1.0 / perc))
    indices = [i for i, zi in zip(indices, z) if z[i] > 0]
    x = x[indices]
    y = y[indices]
    z = z[indices]
    return x, y, z


def get_bodyframes(filename, format_numpy=True):
    with open(filename.replace(".xef", "-bodyframes.json"), "r") as f:
        j = json.load(f)
    if format_numpy:
        return _getdataframefromjsonbodies(j)
    else:
        return j


def _get_dict(jointsframe):
    if jointsframe:
        jointdict = {}
        for k, v in jointsframe.items():
            for coor in ["X", "Y", "Z"]:
                jointdict[k + coor] = v["Position"][coor]
        return jointdict
    else:
        return dict()


def _getdataframefromjsonbodies(bodies, fillna=True):
    jointsframes = [x["Joints"] if x else None for x in bodies]
    d = [_get_dict(x) for x in jointsframes]
    df = pd.DataFrame(d)
    if fillna:
        df = df.fillna(method="pad").fillna(method="backfill")
    return df


"""Detect peaks in data based on their amplitude and other features.
"""


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
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ["falling", "both"]:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[
            np.in1d(
                ind, np.unique(np.hstack((indnan, indnan - 1, indnan + 1))), invert=True
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
        dx = np.min(np.vstack([x[ind] - x[ind - 1], x[ind] - x[ind + 1]]), axis=0)
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

    if show:
        if indnan.size:
            x[indnan] = np.nan
        if valley:
            x = -x
        _plot(x, mph, mpd, threshold, edge, valley, ax, ind)

    return ind


def find_splits(df):
    """
    @arg df: dataframe of skeleton joints
    """
    pca = PCA(n_components=1)
    df_new = pca.fit_transform(df)
    signal = df_new[:, 0]

    fourier = np.fft.fft(signal)
    splitsnb_estimate = np.argmax(abs(fourier[0:20]))

    mpd = len(signal) / (2 * splitsnb_estimate)
    mph = np.mean(signal)

    valleys = _detect_peaks(signal, mpd=mpd, mph=mph, valley=True)
    peaks = _detect_peaks(signal, mpd=mpd, mph=mph)

    return valleys if valleys[0] < peaks[0] else peaks


def get_depthframes(x):
    width = 512
    height = 424
    filename = x.replace(".xef", "-depthframes.dat")
    with open(filename, "rb") as f:
        s = f.read()
    a = array.array("h", s)
    l = len(a) / (height * width)
    b = np.frombuffer(a, dtype=np.dtype("uint16"))
    return np.reshape(b, (l, height, width))


def get_bodyindexframes(x):
    width = 512
    height = 424
    filename = x.replace(".xef", "bodyindexframes.dat")
    with open(filename, "rb") as f:
        s = f.read()
    a = array.array("h", s)
    l = len(a) / (height * width)
    b = np.frombuffer(a, dtype=np.dtype("uint8"))
    return np.reshape(b, (l, height, width))


def validxeffile(x):
    minsizemb = 500
    minfilesize = minsizemb * 1000 * 1000
    return ".xef" in x and os.path.getsize(x) > minfilesize
