# !/usr/bin/env python
# -*- coding: utf-8 -*-
from BasicModule.Region import Region
from BasicModule.VariateKMeans import VariateKMeans
import BasicModule.Math as Math


class POSMIT:

    def __init__(self, trajectoryLs):
        self.cutoff = Math.gaussian(x=3, height=1, center=0, width=1)
        self.chunkSizes = []
        self.computeStats = 1
        self.stats = []
        self.statsAlgo = []
        self.maxStopVariance = 20
        self.stopProbabilities = []
        self.EARTH_RADIUS = 6381372
        self.N = 0  # 所有点的总数
        self.D = trajectoryLs  # 即D, 所有轨迹的列表
        self.numOfEachTra = []  # D中每条轨迹点的总数
        self.allPoints = []  # 所有轨迹的GPS点组成的列表
        self.stopRegionLs = []  # 存放最终停止区域的列表
        self.significantPlacesLs = []
        # 阈值参数
        self.MinStopPro = 0
        self.nSearchRadius = 1
        self.stopVariance = 1
        # 计算所有点的总数，将D拍平
        for trajectory in self.D:
            trajectoryLs = trajectory.T
            self.allPoints += trajectoryLs
            number = len(trajectoryLs)
            self.numOfEachTra.append(number)
            self.N += number

    def setAttribute(self, MinStopPro, nSearchRadius, stopVariance):
        self.MinStopPro = MinStopPro
        self.nSearchRadius = nSearchRadius
        self.stopVariance = stopVariance

    def estimateSearchRadius(self, trajectory, stopVariance):
        trajectoryPoints = trajectory.T
        size = len(trajectoryPoints)
        for i in range(0, size):
            prevIdx = i
            curChunKSize = 1
            i += 1
            for i in range(size):
                trajectoryPoints = trajectory.T
                point_i = trajectoryPoints[i]
                # displacement = self.getEuclideanDistance(prevIdx, i)
                # displacement= trajectory.curveDistance(prevIdx, i)
                displacement = trajectoryPoints[i].distance(trajectoryPoints[prevIdx])
                if displacement <= stopVariance:
                    curChunKSize += 1
                else:
                    break
                prevIdx = i
            if curChunKSize > 1:
                self.chunkSizes.append(curChunKSize)
        if not self.chunkSizes:
            return 1
        searchRadius = Math.mean(self.chunkSizes)
        searchRadius = max(1, round(searchRadius * 0.5))
        return int(searchRadius)

    def score(self, coordsA, coordsB, stopVariance):
        displacementsMeters = 0
        for i in range(0, len(coordsA)):
            displacementsMeters += pow(coordsA[i] - coordsB[i], 2)
        if stopVariance == 0:
            return 0
        return Math.gaussian(displacementsMeters / stopVariance, 1, 0, 1)

    def getStopPr(self, trajectory, centerIdx, nSearchRadius, stopVariance):
        sumWeights = 0
        sumIndexWeight = 0
        trajectoryPoints = trajectory.T
        point_centerIdx = trajectoryPoints[centerIdx]
        # centerCoords=trajectory.getCoords(centerIdx)##获取一个轨迹的经纬度？
        centerCoords = [point_centerIdx.latitude * self.EARTH_RADIUS,
                        point_centerIdx.longitude * self.EARTH_RADIUS]  #############################
        trajectoryPoints = trajectory.T  ##
        size = len(trajectoryPoints)  ##
        lastIdx = size - 1
        bounds = [centerIdx, centerIdx]
        increments = [-1, 1]
        while increments[0] != 0 and increments[1] != 0:
            for i in range(0, len(increments)):
                increment = increments[i]
                if increment == 0:
                    continue
                idx = bounds[i] + increment
                if idx < 0 or idx > lastIdx:
                    increments[i] = 0
                    continue
                indexScore = abs(idx - centerIdx) / nSearchRadius
                indexWeight = Math.gaussian(x=indexScore, height=1, center=0, width=1)
                if indexWeight < self.cutoff:
                    increments[i] = 0
                    continue
                point_idx = trajectoryPoints[idx]
                idxCoords = [point_idx.latitude * self.EARTH_RADIUS, point_idx.longitude * self.EARTH_RADIUS]
                score = self.score(centerCoords, idxCoords, stopVariance)
                sumWeights += indexWeight * score
                sumIndexWeight += indexWeight
                bounds[i] = idx
        return sumWeights / sumIndexWeight

    def run(self, Tid, nSearchRadius, stopVariance):
        stopProbabilities = []
        for trajectory in self.D:
            if trajectory.Tid == Tid:
                trajectoryPoints = trajectory.T
                for i in range(len(trajectoryPoints)):  # 求trajectory长度对吗？
                    # for i in range(0,trajectory.size()):
                    stopProbabilities.append(self.getStopPr(trajectory, i, nSearchRadius, stopVariance))
        return stopProbabilities

    def estimateMinStopPr(self, stopProbabilities):  # 启发式地阈值
        Kmeans_obj = VariateKMeans(stopProbabilities)
        clusters = Kmeans_obj.run(2)
        c1Max = max(clusters[0])
        c2Min = min(clusters[1])
        return c1Max + (c2Min - c1Max) * 0.5

    def findElbowQuick(self, displacement):  # 参见onethreeseven.stopmove.algorithm.Keendle
        if len(displacement) <= 1:
            return 0
        normalisedData = Math.minmaxNormalise1d(Math.gaussianSmooth(displacement, 3))
        for i in range(0, len(normalisedData)):
            normalisedIndex = i / len(displacement)
            normalisedData[i] = normalisedData[i] - normalisedIndex
        bestScore = 0
        elbowIdx = 0
        for i in range(0, len(normalisedData)):
            score = abs(normalisedData[i])
            if score > bestScore:
                bestScore = score
                elbowIdx = i
        return displacement[elbowIdx]

    # 找拐点hd(Spatial stop variance parameter)
    def estimateStopVariance(self, Tid, maxStopVariance):
        displacements = []
        for trajectory in self.D:
            if trajectory.Tid == Tid:
                trajectoryPoints = trajectory.T
                for i in range(1, len(trajectoryPoints) - 1):
                    distance_tmp = trajectoryPoints[i - 1].distance(trajectoryPoints[i])
                    if (distance_tmp > 0) and (distance_tmp < maxStopVariance):
                        displacements.append(distance_tmp)
                displacements.sort()
                # print("displacement为",displacements)
                if len(displacements) > 1:
                    elbow = self.findElbowQuick(displacements)
                    return elbow
        return 0

    def toStopTrajectory(self, Tid, stopProbabilities, minStopProbability):
        SC = []
        for trajectory in self.D:
            if trajectory.Tid == Tid:
                trajectoryPoints = trajectory.T
                for i in range(len(trajectoryPoints)):
                    if stopProbabilities[i] >= minStopProbability:
                        SC.append(i)
        # print("SC的长度为",len(SC))
        return SC

    def POSMIT(self):
        # nSearchRadius=4
        SC = []
        for trajectory in self.D:
            Tid = trajectory.Tid
            # stopVariance = self.estimateStopVariance(Tid=Tid,maxStopVariance=20)
            # print("stopVariance为",stopVariance)
            # nSearchRadius = self.estimateSearchRadius(trajectory,stopVariance)
            # print("nSearchRadius为",nSearchRadius)
            stopProbabilities = self.run(Tid, self.nSearchRadius, self.stopVariance)
            # print("maxStopPro为",max(stopProbabilities))
            # print("stopPros为", stopProbabilities)
            # minStopConfidence=self.estimateMinStopPr(stopProbabilities)##与traj无关
            # minStopConfidence=0.2
            # print("<MinstopPro为",self.minStopConfidence)
            SC.append(self.toStopTrajectory(Tid, stopProbabilities, self.MinStopPro))
        return SC

    # 将聚类结果SC弄成停止区域对象列表StopRegionLs
    def getSignificantPlacesLs(self):
        SC = self.POSMIT()
        print("SC=", SC)
        Rid = 1
        for indexRegion in SC:
            stopRegion = []
            for index in indexRegion:
                stopRegion.append(self.allPoints[index])
            stopRegion_obj = Region(Rid=Rid, region=stopRegion)
            stopRegion_obj.setAttribute()
            self.stopRegionLs.append(stopRegion_obj)
            Rid += 1
        print("StopRegion的总数", len(self.stopRegionLs))
        return self.stopRegionLs
