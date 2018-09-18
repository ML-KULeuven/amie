import pandas as pd
import numpy as np
import data.stickfigure as sf


class Angles:
    def __init__(self, stickfigure):
        self.stickfigure = stickfigure

    def get_angles(self, df):
        angles = pd.DataFrame()
        jd = self.stickfigure.jointtraces(df)
        for left, middle, right in self.stickfigure.jointtriplets():
            try:
                v1 = jd[left] - jd[middle]
                v2 = jd[right] - jd[middle]
                angle = _get_angle(v1, v2)
            except KeyError:
                angle = np.nan
            angles["_".join([left, middle, right])] = angle
        return angles


def _get_angle(v1, v2):
    v1_norm = np.linalg.norm(v1, axis=1)
    v1_u = v1 / np.repeat(v1_norm, 3).reshape([-1, 3])

    v2_norm = np.linalg.norm(v2, axis=1)
    v2_u = v2 / np.repeat(v2_norm, 3).reshape([-1, 3])

    prod = np.sum(v1_u * v2_u, axis=1)
    return np.arccos(np.clip(prod, -1.0, 1.0))


kinect = Angles(sf.kinect)
vicon = Angles(sf.vicon)
