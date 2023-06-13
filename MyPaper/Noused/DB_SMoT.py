# !/usr/bin/env python
# -*- coding: utf-8 -*-
from BasicModule.Region import Region


class DB_SMoT:
    # 初始化参数
    def __init__(self, allTrajectoryLs):
        self.allTrajectoryLs = allTrajectoryLs
        self.trajectory = self.allTrajectoryLs[0]
        self.minTime = 0
        self.minDirChange = 0
        self.maxTol = 0
        # 自己加的
        self.numOfEachTra = []  # allTrajectoryLs中每条轨迹点的总数
        self.allPoints = []  # 所有轨迹的GPS点组成的列表
        self.NumberofAllPts = 0  # 所有点的总数
        self.significantPlacesLs = []  # 存放最终停止区域的列表
        # 计算所有点的总数，将allTrajectoryLs拍平
        for trajectory in self.allTrajectoryLs:
            trajectoryLs = trajectory.T
            self.allPoints += trajectoryLs
            number = len(trajectoryLs)
            self.numOfEachTra.append(number)
            self.NumberofAllPts += number

    # 1 设置参数
    def setAttribute(self, minDirChange, maxTol, minTime):
        self.minDirChange = minDirChange
        self.maxTol = maxTol
        self.minTime = minTime

    # 2 找到以maxTol为公差的的下一个点的坐标
    def lookAhead(self, i):
        nextIndex = i + self.maxTol
        if nextIndex < self.trajectory.N and self.trajectory.variation[nextIndex] > self.minDirChange:
            return nextIndex
        else:
            return nextIndex + i + self.maxTol

    # 3 计算找到的簇的时间
    def timeOfCluster(self, cluster):
        points = cluster
        clusterDuration = 0
        # for i in cluster:
        #     points.append(self.trajectory.T[i])
        if points:
            maxTime = max(points, key=lambda point: point.timeStamp).timeStamp
            minTime = min(points, key=lambda point: point.timeStamp).timeStamp
            clusterDuration = maxTime - minTime
        return clusterDuration

    # 4 核心聚类方法
    def clusterBasedOnDirection(self):
        self.trajectory.setVariationDifferentiation()
        variation = self.trajectory.variation
        n = self.trajectory.N
        clusterOpened = False
        AllClusters = []
        Cluster = []
        i = 0
        while i < n:
            if variation[i] > self.minDirChange:
                Cluster.append(self.allPoints[i])
                clusterOpened = True
            else:
                if clusterOpened:
                    lastIndex = self.lookAhead(i)
                    if lastIndex <= i + self.maxTol:
                        for j in range(i, lastIndex + 1):
                            Cluster.append(self.allPoints[j])
                        i = lastIndex
                    else:
                        if self.timeOfCluster(Cluster) >= self.minTime:
                            # # 排序
                            # Cluster.sort()
                            AllClusters.append(Cluster)
                        Cluster = []
                        clusterOpened = False
            """print("i=", i)
            print("Cluster", Cluster)
            print("AllCluster", AllClusters)"""
            i = i + 1
        # if AllClusters:
        #     AllClusters.sort(key=lambda x: min(x))
        return AllClusters

    # # 5 根据停止区域获得移动区域(停止区域需要从小到大排序)
    # def getMovingRegion(self, S_stop):
    #     # 更新移动区域z
    #     S_moving = []
    #     if S_stop:
    #         S_stop.sort(key=lambda x: min(x))
    #         for i in range(1, len(S_stop)):
    #             movingPoints = []
    #             maxIndex = max(S_stop[i - 1])
    #             minIndex = min(S_stop[i])
    #             for j in range(maxIndex + 1, minIndex):
    #                 movingPoints.append(j)
    #             if movingPoints:
    #                 S_moving.append(movingPoints)
    #         if min(S_stop[0]) != 0:
    #             movingPoints = []
    #             for j in range(min(S_stop[0])):
    #                 movingPoints.append(j)
    #             if movingPoints:
    #                 S_moving.append(movingPoints)
    #         if max(S_stop[-1]) != self.trajectory.N - 1:
    #             movingPoints = []
    #             for j in range(max(S_stop[-1]), self.trajectory.N):
    #                 movingPoints.append(j)
    #             if movingPoints:
    #                 S_moving.append(movingPoints)
    #     else:
    #         S_moving = [x for x in range(self.trajectory.N)]
    #     if S_moving and isinstance(S_moving[0], list):
    #         S_moving.sort(key=lambda x: min(x))
    #     return S_moving
    #
    # # 6 同时返回停止区域和移动区域
    # def getStopMove(self):
    #     stopRegion = self.clusterBasedOnDirection()
    #     movingRegion = self.getMovingRegion(stopRegion)
    #     return stopRegion, movingRegion
    # 6 获得重要地点
    def getSignificantPlacesLs(self):
        resultLs = self.clusterBasedOnDirection()
        Rid = 1
        for SP in resultLs:
            stopRegion_obj = Region(Rid=Rid, region=SP)
            stopRegion_obj.setAttribute()
            self.significantPlacesLs.append(stopRegion_obj)
            Rid += 1
        print("SgnificantPlaces的总数", len(self.significantPlacesLs))
        return self.significantPlacesLs
