import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation
from IPython.display import HTML
import data.stickfigure as sf


class StickFigureDrawer:
    def __init__(
        self, stickfigure, xyzconfig, linewidth=1, interval=50, stepsize=1, figsize=1
    ):
        self.stickfigure = stickfigure
        self.xyzconfig = xyzconfig
        self.linewidth = linewidth
        self.interval = interval
        self.stepsize = 1
        self.figsize = figsize

    def stickfigureanim(self, df, figsize=1):
        # Attaching 3D axis to the figure
        fig = plt.figure(figsize=(figsize * 8, figsize * 5))
        ax = p3.Axes3D(fig)

        # Creating initial skeleton
        # NOTE: Can't pass empty arrays into 3d version of plot()
        lines = self._plotlines(ax, df)
        self._axconfig(ax, df)

        bones = self.stickfigure.bonetraces(df)

        def _update_lines(i, bones, lines):
            for bone, line in zip(bones, lines):
                x, y, z = self._bonexyz(bone, self.stepsize * i)
                # NOTE: there is no .set_data() for 3 dim data...
                line.set_data([x, y])
                line.set_3d_properties(z)
            return lines

        # Creating the Animation object
        line_ani = animation.FuncAnimation(
            fig,
            _update_lines,
            int(len(df) / self.stepsize),
            fargs=(bones, lines),
            interval=self.interval,
            blit=True,
        )

        return HTML(line_ani.to_html5_video())

    def stickfigureplot(self, df, figsize=1, show=True, linewidth=None):

        # Attaching 3D axis to the figure
        fig = plt.figure(figsize=(figsize * 7, figsize * 5))
        ax = p3.Axes3D(fig)

        if not linewidth:
            linewidth = self.linewidth

        self._plotlines(ax, df, linewidth)
        self._axconfig(ax, df)

        if show:

            plt.show()

    def stickfigureplot5(self, df, figsize=1, show=True, linewidth=None):
        fig = plt.figure(figsize=(figsize * 7 * 5, figsize * 5))

        if not linewidth:
            linewidth = self.linewidth

        stepsize = len(df) // 5
        for i in range(5):
            ax = fig.add_subplot(1, 5, i + 1, projection="3d")
            self._plotlines(ax, df[i * stepsize :], linewidth)
            self._axconfig(ax, df[i * stepsize :])

        if show:
            plt.show()

    def _plotlines(self, ax, df, linewidth=None):
        lines = []
        bones = self.stickfigure.bonetraces(df)
        for bone in bones:
            x, y, z = self._bonexyz(bone)
            if not linewidth:
                linewidth = self.linewidth
            line = ax.plot(x, y, z, color="blue", linewidth=linewidth)
            lines.append(line[0])
        return lines

    def _bonexyz(self, bone, i=0):
        coords = []
        for joint in bone.values():
            j = []
            for x in self.xyzconfig:
                v = self.posorneg(joint, x).values[i]
                j.append(v)
            coords.append(j)
        return zip(*coords)

    def posorneg(self, df, column):
        if "-" not in column:
            v = df[column]
        else:
            v = -df[column[1:]]
        return v

    def _axconfig(self, ax, df):
        # Setting the axes properties
        joints = self.stickfigure.jointtraces(df)
        xs, ys, zs = [], [], []
        for j in joints.values():
            xs += list(self.posorneg(j, self.xyzconfig[0]))
            ys += list(self.posorneg(j, self.xyzconfig[1]))
            zs += list(self.posorneg(j, self.xyzconfig[2]))
        avgx, avgy, avgz = np.nanmean(xs), np.nanmean(ys), np.nanmean(zs)
        stdx, stdy, stdz = np.nanstd(xs), np.nanstd(ys), np.nanstd(zs)
        # print(avgx,avgy,avgz)
        space = stdx + stdy + stdz
        ax.set_xlim3d([avgx - space, avgx + space])
        ax.set_xlabel(self.xyzconfig[0])

        ax.set_ylim3d([avgy - space, avgy + space])
        ax.set_ylabel(self.xyzconfig[1])

        ax.set_zlim3d([avgz - space, avgz + space])
        ax.set_zlabel(self.xyzconfig[2])


kinect = StickFigureDrawer(sf.kinect, ["-Z", "X", "Y"], linewidth=5)
vicon = StickFigureDrawer(
    sf.vicon, ["X", "Y", "Z"], linewidth=1.1, interval=20, stepsize=20
)
