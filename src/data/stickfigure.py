import itertools
import pandas as pd


class StickFigure:
    def __init__(self, bones):
        self.bones = bones

    def joints(self):
        return set([joint for bone in self.bones for joint in bone])

    def _jointtriplets_of_joint(self, joint):
        c_joints = []
        for jointA, jointB in self.bones:
            if jointA == joint:
                c_joints.append(jointB)
            if jointB == joint:
                c_joints.append(jointA)

        return [
            (a, joint, b) for (a, b) in itertools.combinations(c_joints, 2)
        ]

    def jointtriplets(self):
        jointtriplets = []
        for j in self.joints():
            jointtriplets += self._jointtriplets_of_joint(j)
        return jointtriplets

    def jointtraces(self, df):
        jd = {}
        for joint in self.joints():
            if joint + "X" in df.columns:
                jdf = df[[joint + "X", joint + "Y", joint + "Z"]]
                jdf.columns = ["X", "Y", "Z"]
                jd[joint] = jdf
        return jd

    def bonetraces(self, df):
        jd = self.jointtraces(df)

        bones = []
        for j1, j2 in self.bones:
            if j1 in jd.keys() and j2 in jd.keys():
                bone = {}
                bone[j1] = jd[j1]
                bone[j2] = jd[j2]
                bones.append(bone)
        return bones

    # changing representation of stickfigures from rows to dataframes
    def _row_to_df(self, row):
        data = []
        for joint in self.joints():
            data.append(
                [
                    joint,
                    row[joint + "X"].values[0],
                    row[joint + "Y"].values[0],
                    row[joint + "Z"].values[0],
                ]
            )
        return pd.DataFrame(data=data, columns=["joint", "X", "Y", "Z"])

    def _df_to_row(self, df):
        data = {}
        for joint, values in df.groupby("joint"):
            for coor in ["X", "Y", "Z"]:
                data[joint + coor] = values[coor].values[0]
        return pd.DataFrame([data])

    def rows_to_dataframes(self, rows):
        dfs = rows.groupby(rows.index)
        newdfs = dfs.apply(self._row_to_df)
        return [
            v for k, v in newdfs.groupby([fst for fst, snd in newdfs.index])
        ]

    def dataframes_to_rows(self, dfs):
        return pd.concat([self._df_to_row(df) for df in dfs])


kinect = StickFigure(
    [
        # torso
        ("Head", "Neck"),
        ("Neck", "SpineShoulder"),
        ("SpineShoulder", "SpineMid"),
        ("SpineMid", "SpineBase"),
        ("SpineShoulder", "ShoulderRight"),
        ("SpineShoulder", "ShoulderLeft"),
        ("SpineBase", "HipRight"),
        ("SpineBase", "HipLeft"),
        # Right Arm
        ("ShoulderRight", "ElbowRight"),
        ("ElbowRight", "WristRight"),
        ("WristRight", "HandRight"),
        ("HandRight", "HandTipRight"),
        ("WristRight", "ThumbRight"),
        # Left Arm
        ("ShoulderLeft", "ElbowLeft"),
        ("ElbowLeft", "WristLeft"),
        ("WristLeft", "HandLeft"),
        ("HandLeft", "HandTipLeft"),
        ("WristLeft", "ThumbLeft"),
        # Right Leg
        ("HipRight", "KneeRight"),
        ("KneeRight", "AnkleRight"),
        ("AnkleRight", "FootRight"),
        # Left Leg
        ("HipLeft", "KneeLeft"),
        ("KneeLeft", "AnkleLeft"),
        ("AnkleLeft", "FootLeft"),
    ]
)

vicon = StickFigure(
    [
        # right arm
        ("RHAND", "RWRB"),
        ("RHAND", "RWRA"),
        ("RWRA", "RWRRB"),
        ("RWRA", "RELB"),
        ("RWRA", "RELBM"),
        ("RWRB", "RELB"),
        ("RWRB", "RELBM"),
        ("RELB", "RSHO"),
        ("RELBM", "RSHO"),
        # left arm
        ("LHAND", "LWRB"),
        ("LHAND", "LWRA"),
        ("LWRA", "LWRRB"),
        ("LWRA", "LELB"),
        ("LWRA", "LELBM"),
        ("LWRB", "LELB"),
        ("LWRB", "LELBM"),
        ("LELB", "LSHO"),
        ("LELBM", "LSHO"),
        # chest
        ("RSHO", "LSHO"),
        ("CLAV", "RSHO"),
        ("CLAV", "LSHO"),
        ("CLAV", "STRN"),
        ("CLAV", "T10"),
        ("T10", "RPSI"),
        ("T10", "LPSI"),
        ("STRN", "RASI"),
        ("STRN", "LASI"),
        ("T10", "RSHO"),
        ("T10", "LSHO"),
        ("RPSI", "RASI"),
        ("LPSI", "LASI"),
        ("LASI", "RASI"),
        ("LPSI", "RPSI"),
        ("LPSI", "RASI"),
        ("LASI", "RPSI"),
        # ("CLAV","LASI"),
        # ("CLAV","RASI"),
        # right leg:
        ("RASI", "RTHI"),
        ("RPSI", "RTHI"),
        ("RTHI", "RKNEM"),
        ("RASI", "RKNEM"),
        ("RPSI", "RKNEM"),
        ("RTHI", "RKNE"),
        ("RASI", "RKNE"),
        ("RPSI", "RKNE"),
        ("RKNE", "RTIB"),
        ("RKNEM", "RTIB"),
        ("RKNE", "RHEE"),
        ("RKNEM", "RHEE"),
        ("RTIB", "RHEE"),
        ("RHEE", "RMTP5"),
        ("RHEE", "RMTP1"),
        # left leg:
        ("LASI", "LTHI"),
        ("LPSI", "LTHI"),
        ("LTHI", "LKNEM"),
        ("LASI", "LKNEM"),
        ("LPSI", "LKNEM"),
        ("LTHI", "LKNE"),
        ("LASI", "LKNE"),
        ("LPSI", "LKNE"),
        ("LKNE", "LTIB"),
        ("LKNEM", "LTIB"),
        ("LKNE", "LHEE"),
        ("LKNEM", "LHEE"),
        ("LTIB", "LHEE"),
        ("LHEE", "LMTP5"),
        ("LHEE", "LMTP1"),
    ]
)
"""



"""
