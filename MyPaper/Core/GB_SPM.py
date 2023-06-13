# !/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import itertools
from BasicModule.Region import Region
from time import *


class GB_SPM:
    def __init__(self, trajectory):
        # 1、判断为特征点需要的参数
        self.vt = 0  # 速度阈值
        # 2、判断停止区域需要的参数
        # self.eps = 0
        self.hi = 0
        # self.alpha = 1
        self.aveCPDis = 0  # 特征点的平均距离
        self.mergeDis = 0  # 合并簇的距离
        self.R = 0  # 判断检索邻域的半径
        # 3、自身的一些结果
        self.tr = trajectory
        self.allPts = trajectory.T  # 所有轨迹的列表
        self.N = len(self.allPts)  # 轨迹点的总数
        self.aveAllDis = self.tr.curveDistance(0, self.N - 1) / self.N  # 所有轨迹点的平均距离
        self.allCPLs = []  # 所有的特征点组成的列表
        self.NCP = 0  # self.allCPLs的长度
        self.SPDLs = []  # 最终结果
        self.significantPlacesLs = []
        self.meanCPDis = 0
        self.nVelocityLs = []  # 保存领域速度的列表
        # 4、图的一些属性
        self.density = []  # 点v包含的点的数目
        print("所有轨迹点的平均距离=", self.aveAllDis)
        # 5、优化距离计算
        self.calculatedDis = dict()

    # 方法1.1：设置参数
    def setAttribute(self, hi, vt):
        self.hi = hi
        self.vt = vt

    # 方法1.2：求点pj在所有点中的索引领域(返回结果包括pi)
    def indexNeiborOfAll(self, pj):
        indexN = [pj]
        delta = 3 * self.hi
        # 找点pi左边的领域
        leftPk = pj
        rightPk = leftPk
        pi = 1
        while pi <= delta:
            if leftPk - pi >= 0:
                leftPk -= 1
                indexN.append(leftPk)
                pi += 1
            else:
                break  # 防止无限循环
        pi = 1
        while pi <= delta:
            if rightPk + pi <= self.N - 1:
                rightPk += 1
                indexN.append(rightPk)
                pi += 1
            else:
                break  # 防止无限循环
        return indexN

    # 方法1.3：求点pj在特征点中除了pi的eps领域
    def epsNeibor(self, pj, eps):
        N_pi = []
        CP_N = len(self.allCPLs)
        # 找点pi左边的领域
        pk = self.allCPLs.index(pj)
        if pk - 1 >= 0:
            distance = self.allPts[self.allCPLs[pk - 1]].distance(self.allPts[self.allCPLs[pk]])
            while distance <= eps:
                N_pi.append(self.allCPLs[pk - 1])
                pk = pk - 1
                if pk - 1 >= 0:
                    distance = distance + self.allPts[self.allCPLs[pk - 1]].distance(self.allPts[self.allCPLs[pk]])
                else:
                    break  # 防止因距离不够而导致无限循环
        # 找pi右边的eps领域
        pk = self.allCPLs.index(pj)
        if pk + 1 <= CP_N - 1:
            distance = self.allPts[self.allCPLs[pk]].distance(self.allPts[self.allCPLs[pk + 1]])
            while distance <= eps:
                N_pi.append(self.allCPLs[pk + 1])
                pk = pk + 1
                if pk + 1 <= CP_N - 1:
                    distance = distance + self.allPts[self.allCPLs[pk]].distance(self.allPts[self.allCPLs[pk + 1]])
                else:
                    break  # 防止因距离不够而导致无限循环
        return N_pi

    # 方法1.4：求点pj在特征点集合的索引领域(返回结果不包括pj)
    def indexNeiborOfCP(self, pj):
        indexN = []
        delta = 3 * self.hi
        # 找点pi左边的领域
        leftPk = self.allCPLs.index(pj)
        rightPk = leftPk
        pi = 1
        while pi <= delta:
            if leftPk - pi >= 0:
                leftPk -= 1  #
                indexN.append(self.allCPLs[leftPk])
                pi += 1
            else:
                break  # 防止无限循环
        pi = 1
        while pi <= delta:
            if rightPk + pi <= self.NCP - 1:
                rightPk += 1  #
                indexN.append(self.allCPLs[rightPk])
                pi += 1
            else:
                break  # 防止无限循环
        return indexN

    # 方法1.5：求CalculatedDis，并返回相应的距离
    def getCalculatedDis(self, vi, vj):
        disKey = str(vi) + "_" + str(vj)
        if not self.calculatedDis.get(disKey):
            distance_ij = self.allPts[vi].distance(self.allPts[vj])
            self.calculatedDis[disKey] = distance_ij
        else:
            distance_ij = self.calculatedDis[disKey]
        return distance_ij

    # 方法2: 提取特征点CP
    def extractCP(self):
        begin_time = time()
        for pi in range(self.N):
            N_pi = self.indexNeiborOfAll(pi)
            pStart = min(N_pi)
            pEnd = N_pi[-1]
            curveDis = 0
            pCount = pStart  # 代替PStart自增求curveDis
            # 求curveDis
            while pCount < pEnd:
                curveDis += self.getCalculatedDis(pCount, pCount + 1)
                pCount = pCount + 1
            # 求dutation
            duration = self.allPts[pEnd].timeStamp - self.allPts[pStart].timeStamp
            # 求领域速度
            if duration != 0:
                v_pi = curveDis / duration
            else:
                v_pi = (self.allPts[pStart].velocity + self.allPts[pEnd].velocity) / 2
            if v_pi >= 17:  # 速度所阈值
                v_pi = -0.1
            self.nVelocityLs.append(v_pi)
            # 判断阈值是否小于self.vt
            if v_pi <= self.vt:
                self.allCPLs.append(pi)
        end_time = time()
        print("提取特征点耗费的时间=", end_time - begin_time)
        # 计算特征点的平均距离averageDis
        self.NCP = len(self.allCPLs)
        for i in range(self.NCP - 1):
            self.aveCPDis += self.allPts[self.allCPLs[i]].distance(self.allPts[self.allCPLs[i + 1]])
        self.aveCPDis = self.aveCPDis / self.NCP
        print("特征点的[数量, 平均距离]", [self.NCP, self.aveCPDis])
        # print("allCPLs", self.allCPLs)

    # 方法3: 聚类
    # 方法3.1：算点vi的总电势(总电势代表点的局部密度)
    def potential(self, vi, pi_vi):
        totalPotential = 0
        for vj in pi_vi:
            distance_ij = self.getCalculatedDis(vi, vj)
            totalPotential += distance_ij
        return totalPotential

    # 方法3.2：算stayTime
    def stayTime(self, vi, pi_vi):
        copy_pi_vi = pi_vi.copy()
        copy_pi_vi.append(vi)
        copy_pi_vi = sorted(copy_pi_vi)
        N = len(copy_pi_vi)
        st_vi = 0
        if N >= 2:
            st_vi = self.tr.TSDuration(copy_pi_vi[-1], copy_pi_vi[0])
        if N == 1:
            st_vi = 0
        return st_vi

    # 方法3.3：获取每个点最大的updateLable
    def updateLable(self, vi, labelDict):
        pi_vi = self.indexNeiborOfCP(vi)  # 这里需要修改
        density_vi = self.potential(vi, pi_vi)
        self.density.append((vi, density_vi))
        st_vi = self.stayTime(vi, pi_vi)
        maxW = 0
        if len(pi_vi) > 0:
            maxI = pi_vi[0]
            wLs = []
            for vj in pi_vi:
                pi_vj = self.indexNeiborOfCP(vj)  # 这里需要修改
                density_vj = self.potential(vj, pi_vj)
                st_vj = self.stayTime(vj, pi_vj)
                # 开始计算一些需要的变量
                deltaDensity = abs(density_vi - density_vj)
                distance_ij = self.getCalculatedDis(vi, vj)
                st_ij = 1 / 2 * (st_vi + st_vj)
                w_ij = math.exp(-(deltaDensity + distance_ij)) * st_ij
                wLs.append(w_ij)
                if w_ij > maxW:
                    maxW = w_ij
                    maxI = vj
        else:
            maxI = vi
        return labelDict[maxI]

    # 方法3.4：合并相交的簇，最短距离≤alpha * eps的簇合并
    def mergerIntersectingSP(self):
        begin_time = time()
        SPIndex = 0
        print("合并半径=", self.mergeDis)
        while SPIndex <= len(self.SPDLs) - 2:
            SPi = self.SPDLs[SPIndex]
            SPj = self.SPDLs[SPIndex + 1]
            # 把第一个簇的最后一个点的与第二个簇第一个点的距离近似当成簇间最小距离
            minDistbetweenSP = self.allPts[SPi[-1]].distance(self.allPts[SPj[0]])
            # 最小距离<=1/2*eps则合并
            if minDistbetweenSP <= self.mergeDis:
                self.SPDLs[SPIndex + 1] = self.SPDLs[SPIndex] + self.SPDLs[SPIndex + 1]  # SPj = SPi 前一个后移
                del self.SPDLs[SPIndex]
                SPIndex -= 1
            SPIndex += 1
        end_time = time()
        print("合并簇耗费的时间=", end_time - begin_time)
        # 将合并后的簇中的下标替换成对应的GPS点
        for i in range(len(self.SPDLs)):
            tempPLs = []
            for vi in self.SPDLs[i]:
                tempPLs.append(self.allPts[vi])
                self.SPDLs[i] = tempPLs
        self.SPDLs.sort(key=lambda x: x[0].TIndex)

    # 方法3.5：标签传播
    def SPD(self):
        self.extractCP()
        # Dataset1: 1.5  Dataset2: 6
        self.mergeDis = 1.5 * self.hi * self.aveCPDis  # 这里控制合并的半径,间接控制SI
        # self.mergeDis = 50 * self.aveCPDis  # //4  0.733,0.512
        self.R = self.hi * self.aveCPDis
        densityLs = []
        # set a unique lable for each node
        labelDict = {}
        labelCount = 1
        for vi in self.allCPLs:
            labelDict[vi] = labelCount
            labelCount += 1
            # pi_vi = self.epsNeibor(vi, self.eps)
            pi_vi = self.indexNeiborOfCP(vi)  # 这里需要改
            # density_vi = len(pi_vi)  # 当pi_vi =[]时，density_vi =0
            density_vi = self.potential(vi, pi_vi)
            densityLs.append((vi, density_vi))
        # orderList <- setUpdateOrder({v1,v2,...,vNv})
        # print(densityLs)
        begin_time = time()
        sortLs = sorted(densityLs, key=lambda items: items[1], reverse=True)  # (vi, density_vi)
        # print("sortLs=", sortLs)
        orderLs = [x[0] for x in sortLs]  # 按密度降序排序的vi下标
        isChange = 1
        count = 0
        # while isChange == 1:  # 这里控制循环次数,即n_{ite}
        for pi in range(len(orderLs)):
            vi = orderLs[pi]
            label_vi = labelDict[vi]
            count = 0
            updateLabel = self.updateLable(vi, labelDict)
            if updateLabel != label_vi:
                labelDict[vi] = updateLabel
                count += 1
            # if count == 0:
            #     isChange = 0
        # place the nodes with the same label in one cluster Ci
        labelDict_order = dict(sorted(labelDict.items(), key=lambda x: x[1]))
        groupC = [list(group) for key, group in itertools.groupby(labelDict_order.items(), key=lambda v: v[1])]
        for c in groupC:
            tempResult = []
            for item in c:
                tempResult.append(item[0])
            self.SPDLs.append(tempResult)
        end_time = time()
        print("标签传播耗费的时间=", end_time - begin_time)
        # 合并
        self.mergerIntersectingSP()
        return self.SPDLs

    # 方法3.6：将聚类结果SPDLs弄成停止区域对象列表SignificantPlacesLs
    def getSignificantPlacesLs(self):
        SPDLs = self.SPD()
        Rid = 1
        for SP in SPDLs:
            stopRegion_obj = Region(Rid=Rid, region=SP)
            stopRegion_obj.setAttribute()
            if stopRegion_obj.totalPoints >= 4 and stopRegion_obj.R <= 20:  # 这里控制精度
                self.significantPlacesLs.append(stopRegion_obj)
                Rid += 1
        print("SgnificantPlaces的总数", len(self.significantPlacesLs))
        return self.significantPlacesLs
