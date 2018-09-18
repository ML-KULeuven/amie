import numpy as np
import numpy.linalg


def linear_transform(df1, df2):
    a = df1[["X", "Y", "Z"]].values
    b = df2[["X", "Y", "Z"]].values
    A = np.append(a.T, np.ones(len(a))).reshape((len(a[0]) + 1, -1)).T
    x, res, rank, s = numpy.linalg.lstsq(A, b)
    error = np.sqrt(np.sum([r ** 2 for r in res]))
    new_a = np.dot(A, x)
    df3 = df1.copy()
    df3[["X", "Y", "Z"]] = new_a
    return error, df3


def linear_transform_error(df1, df2, rcond=-1):
    a = df1[["X", "Y", "Z"]].values
    b = df2[["X", "Y", "Z"]].values
    A = np.append(a.T, np.ones(len(a))).reshape((len(a[0]) + 1, -1)).T
    res = numpy.linalg.lstsq(A, b, rcond=rcond)[1]
    return np.sqrt(np.sum([r ** 2 for r in res]))


def linear_transform_matrix(df1, df2, rcond=-1):
    a = df1[["X", "Y", "Z"]].values
    b = df2[["X", "Y", "Z"]].values
    A = np.append(a.T, np.ones(len(a))).reshape((len(a[0]) + 1, -1)).T
    x, res, rank, s = numpy.linalg.lstsq(A, b, rcond=rcond)
    return x
