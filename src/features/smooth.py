import numpy as np


def fourier(df, frequencies=50):
    def f(y):
        ft = np.fft.fft(y)
        ftabs = np.abs(ft)
        idx = np.argsort(ftabs)[::-1]
        for i in idx[frequencies:]:
            ft[i] = 0  # Note, rft.shape = 21
        return np.real(np.fft.ifft(ft))

    return df.apply(f)
