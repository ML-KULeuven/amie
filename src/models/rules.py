class RuleClassifier:
    def __init__(self, kot_t=0, kk_t=0.10, ftl_t=0.20, poses=3):

        self.kot_t = kot_t
        self.kk_t = kk_t
        self.ftl_t = ftl_t
        self.poses = poses

    def fit(self, X, y):
        self.X = X
        self.y = y
        return self

    def is_kot(self, df):
        # KOT rule: (kneeleftz + kneeleftrightz) smaller than
        # footleftz and knee
        leftkot = (df.KneeLeftZ - df.FootLeftZ) < self.kot_t
        rightkot = (df.KneeRightZ - df.FootRightZ) < self.kot_t
        return sum(leftkot & rightkot)

    def is_kk(self, df):
        # KK rule: abs((kneeleftX - kneerightY)) < threshold
        kk = abs(df.KneeLeftX - df.KneeRightX) < self.kk_t
        return sum(kk)

    def is_ftl(self, df):
        # FTL rule: SpineBaseZ - SpineShoulderZ > threshhold
        ftl = df.SpineShoulderZ < (df.SpineBaseZ - self.ftl_t)
        return sum(ftl)

    def predict1(self, df):

        scores = [self.poses, self.is_kot(df), self.is_kk(df), self.is_ftl(df)]
        labels = [1, 2, 3, 4]
        return max(zip(scores, labels), key=lambda x: x[0])[1]

    def predict(self, dfs):
        return [self.predict1(df) for df in dfs]

    def get_params(self, deep=True):
        return self.__dict__

    def set_params(self, **d):
        self.__dict__ = d
        return self
