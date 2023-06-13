# !/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from Visualization.Colors import colorNames


class PlotTools:
    def __init__(self, rawTsLs, stopRegionLs):
        self.colors = list(colorNames.keys())
        self.outputPath = "Results\\Figure\\"
        self.rawTsLs = rawTsLs
        self.rawX = []
        self.rawY = []
        self.stopRegionLs = stopRegionLs
        self.stopRegionsX = []  # 这里stopRegionsX是二维的
        self.stopRegionsY = []  # 这里stopRegionsY是二维的

    # 方法1：将原始轨迹和最终的停止区域的点转化为画图要用的[x, y]坐标
    def transferToXY(self):
        for Ts in self.rawTsLs:
            for point in Ts:
                self.rawX.append(point.x)
                self.rawY.append(point.y)
        for stopRegion in self.stopRegionLs:
            tempX = []
            tempY = []
            stopRegionPts = stopRegion.region
            for point in stopRegionPts:
                tempX.append(point.x)
                tempY.append(point.y)
            self.stopRegionsX.append(tempX)
            self.stopRegionsY.append(tempY)

    # 方法2：画散点图
    def plotScatter(self, fileName):
        """plt.title(name)
        c1 = plt.plot(X0, X1, c='blue')
        plt.scatter(x,y,c='b','marker'='o',linewidths=1)，其中c为color颜色，marker为点的形状('o'为circle表示圆)
        在调用最后的plt.show或plt.save方法前，按顺序吧plt.scatter()的内容依次标记在一张图上"""
        plt.scatter(self.rawX, self.rawY, c='blue', marker="o")  # rawPlt
        cnt = 0
        for index in range(len(self.stopRegionLs)):
            plt.scatter(self.stopRegionsX[index], self.stopRegionsY[index], c=self.colors[cnt % len(self.colors)],
                        linewidths=1)  # resultPlt
            cnt = cnt + 1
        # plt.savefig(self.outputPath + fileName)
        # plt.savefig(self.outputPath + fileName + ".pdf")
        plt.show()
        plt.close()

    # 方法3：自动加标签
    @staticmethod
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                plt.text(rect.get_x() + rect.get_width() / 2. - 0.25, 1.01 * height, '%.3f' % height)
            else:
                plt.text(rect.get_x() + rect.get_width() / 2. - 0.25, 1.15 * height, '%.3f' % height)
                # plt.text(rect.get_x() + rect.get_width() / 2. - 0.25, 1.07 * height, '%.3f' % height)

    # 方法4：画折线图图
    @staticmethod
    def plotLine(dataLs):
        dataX = []
        dataY = dataLs
        for i in range(len(dataY)):
            dataX.append(i)
        plt.plot(dataX, dataY, c='k', linewidth=1)
        # 全屏展示
        manager = plt.get_current_fig_manager()
        manager.window.showMaximized()
        plt.show()

    # 方法5：保存折线图
    @staticmethod
    def saveLine(dataLs, fileName):
        dataX = []
        dataY = dataLs
        for i in range(len(dataY)):
            dataX.append(i)
        plt.plot(dataX, dataY, c='k', linewidth=1)
        # 调整大小
        # fig = plt.gcf()
        # fig.subplots_adjust(right=0.7)
        # fig.set_size_inches(50, 30)
        plt.savefig("F:\\用户\\Desktop\\速度图\\" + fileName)
