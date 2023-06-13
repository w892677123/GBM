# !/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from BasicModule.Region import Region


class CB_SMoT:
    # 初始化参数
    def __init__(self, allTrajectoryLs):
        self.allTrajectoryLs = allTrajectoryLs
        self.trajectory = self.allTrajectoryLs[0]
        self.minTime = 0
        # self.q = 0
        self.eps = 0
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

    # 设置参数
    def setAttribute(self, eps, minTime):
        self.minTime = minTime
        # self.q = q
        # self.eps = self.trajectory.F_q_u_sigma(self.q, self.trajectory.u, self.trajectory.sigma)
        self.eps = eps
        print("CB eps: ", self.eps)

    # 1 判断该点是否是核心点，和该领域是否满足最小停留时间
    # 通过EPS和MinTime限制速度
    def isCorePoint(self, Neighbors):
        points = []
        neighborsDuration = 0
        for i in Neighbors:
            points.append(self.trajectory.T[i])
        if points:
            maxTime = max(points, key=lambda point: point.timeStamp).timeStamp
            minTime = min(points, key=lambda point: point.timeStamp).timeStamp
            neighborsDuration = maxTime - minTime
        if neighborsDuration >= self.minTime:
            return True
        else:
            return False

    # 2  基于速度的停止区域聚类
    def clusterBasedOnVelocity(self):
        S_stop = []
        # newEps = self.epsAdjustment(eps)
        visited = []  # 初始时已访问对象列表为空
        unvisited = [x for x in range(self.trajectory.N)]  # 初始时将所有点标记为未访问
        # 开始聚类
        while len(unvisited) > 0:  # 如果有未访问的点，则访问
            StopPoints = []
            pj = random.choice(list(unvisited))  # 从未访问的点中随机抽取一个点
            # set没有下标访问，所以这里要转换为list
            visited.append(pj)  # 添加入已经访问的列表
            unvisited.remove(pj)  # 从未访问列表中移除
            Neighbors = self.trajectory.Neibor(pj, self.eps)  # 获取pj的领域(原来叫NEps,现在叫Neibor)
            if self.isCorePoint(Neighbors) is True:
                StopPoints.append(self.allPoints[pj])
                for pk in Neighbors:
                    if pk in unvisited:
                        StopPoints.append(self.allPoints[pk])
                        # 更新未访问点
                        visited.append(pk)
                        unvisited.remove(pk)
            if StopPoints:
                # StopPoints.sort()
                S_stop.append(StopPoints)
        # # 排序
        # if S_stop:
        #     S_stop.sort(key=lambda x: min(x))
        return S_stop

    # # 3 根据停止区域获得移动区域
    # def getMovingRegion(self, S_stop):
    #     # 更新移动区域
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
    # # 4 同时返回停止区域和移动区域
    # def getStopMove(self):
    #     stopRegion = self.clusterBasedOnVelocity()
    #     movingRegion = self.getMovingRegion(stopRegion)
    #     return stopRegion, movingRegion
    # 6 获得重要地点
    def getSignificantPlacesLs(self):
        resultLs = self.clusterBasedOnVelocity()
        Rid = 1
        for SP in resultLs:
            stopRegion_obj = Region(Rid=Rid, region=SP)
            stopRegion_obj.setAttribute()
            self.significantPlacesLs.append(stopRegion_obj)
            Rid += 1
        print("SgnificantPlaces的总数", len(self.significantPlacesLs))
        return self.significantPlacesLs
