from dtaidistance import dtw
from tqdm import tqdm
import numpy as np


def distance_matrix(examples):
    columns = examples[0].columns
    dists = []
    for c in tqdm(columns):
        timeseries = [df[c].values for df in examples]
        dist = dtw.distance_matrix_fast(timeseries, max_dist=2000)
        dists.append(dist)
    m = sum_matrices(dists)
    return mirror_matrix(m)


def sum_matrices(ms):
    tm = ms[0].copy()
    for i in range(1, len(ms)):
        tm += ms[i]
    return tm


def mirror_matrix(m):
    m1 = m.copy()
    n = len(m)
    for i in range(0, n):
        for j in range(i, n):
            m1[j, i] = m1[i, j]
    return m1


def printm(m):
    for row in m:
        print(["%.1f" % x for x in row])


class DTWClassifier:
    def __init__(self, dmpath):
        self.dmpath = dmpath

    def fit(self, train_index, y):
        self.dm = np.load(self.dmpath)
        self.train_index = train_index
        self.y = y

    def predict(self, test_index):
        return [self.predict1(i) for i in test_index]

    def predict1(self, i):
        row = self.dm[i][self.train_index]
        j = np.argmin(row)
        return self.y[j]

    def get_params(self, deep=True):
        return {"dmpath": self.dmpath}

    def set_params(self, d):
        self.dmpath = d["dmpath"]
