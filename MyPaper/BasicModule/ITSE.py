# !/usr/bin/env python
# -*- coding: utf-8 -*-
from BasicModule.TS import TS
import time


# from collections import Counter  # 用来判断重复元素及其重复次数的包 Counter()


class ITSE:
    def __init__(self, allCPLs, n_grid, gt):
        self.allCPLs = allCPLs  # 所有特征点的集合
        self.timePtsLs = []  # 所有点的时间集合
        self.n_grid = n_grid  # 将时间划分的数量
        self.gt = gt  # density threshold
        self.TSS = []  # 存放TS的集合
        self.HTSS = []  # hight TS set
        self.LTSS = []  # low TS set
        self.ITSS = []  # 合并完后的最终的intensive TS set

    # 方法1：找出相邻的高密度HTS：
    def getAdjacentHTS(self):
        findHTS = []  # 暂时找到的相邻结果，二维列表
        HTSSIndexLs = [i for i in range(len(self.HTSS))]
        adjacentIndexLs = []
        index = 1
        lenOfHTSS = len(self.HTSS)
        breakFlag = False
        isLastBreakFlag = False
        while index <= lenOfHTSS - 1:
            if self.HTSS[index].TSId - self.HTSS[index - 1].TSId == 1:
                flag = index - 1
                while self.HTSS[index].TSId - self.HTSS[index - 1].TSId == 1:
                    if index + 1 == lenOfHTSS - 1:  # 此时index为倒数第二个
                        breakFlag = True
                        break
                    elif index == lenOfHTSS - 1:  # 此时index为倒数第一个
                        findHTS.append(self.HTSS[flag:index + 1])
                        adjacentIndexLs += HTSSIndexLs[flag:index + 1]
                        isLastBreakFlag = True
                        break
                    else:
                        index += 1
                # 开始单独判断倒数第二个和最后一个的关系
                if breakFlag:  # index = len - 1 - 1, 倒数第二个
                    index += 1  # 此时index= len - 1，最后一个
                    if self.HTSS[index].TSId - self.HTSS[index - 1].TSId == 1:
                        # 若最后一个和倒数第二个连续，则加入后结束
                        findHTS.append(self.HTSS[flag:index + 1])
                        adjacentIndexLs += HTSSIndexLs[flag:index + 1]
                    else:
                        # 若最后一个和倒数第二个不连续，则先加入到倒数第二个
                        findHTS.append(self.HTSS[flag:index])
                        adjacentIndexLs += HTSSIndexLs[flag:index]
                        # 再加入最后一个独立成的列表
                        findHTS.append(self.HTSS[index:index + 1])
                        adjacentIndexLs += HTSSIndexLs[index:index + 1]
                    break
                # index为倒数第一个
                elif isLastBreakFlag:
                    break
                # index不为倒数第二个，也不为倒数第一个
                else:
                    findHTS.append(self.HTSS[flag:index - 1])
                    adjacentIndexLs += HTSSIndexLs[flag:index - 1]
            else:
                index += 1
        leftIndexLs = list((set(HTSSIndexLs) - set(adjacentIndexLs)))
        for index in leftIndexLs:
            findHTS.append([self.HTSS[index]])
        # 重新排序
        findHTS.sort(key=lambda HTSelement: HTSelement[0].TSId)
        return findHTS

    # 方法2：得到所有点的时间集合，然后进行密集时间划分
    def ITSExtraction(self):
        # 排序
        self.allCPLs.sort(key=lambda CPt: CPt.timeStamp)
        for CP in self.allCPLs:
            self.timePtsLs.append(CP.timeStamp)
        timeInterval = (self.timePtsLs[-1] - self.timePtsLs[0]) / self.n_grid
        print("timeLength=", self.timePtsLs[-1] - self.timePtsLs[0])
        print("timeInterval=", timeInterval)
        cntNgrid = 0
        CPLs = []
        startTime = self.timePtsLs[0]
        CPIndex = 0
        previousIndexLs = []
        while CPIndex <= len(self.timePtsLs) - 1:
            if cntNgrid < self.n_grid - 1:
                if self.timePtsLs[CPIndex] <= startTime + timeInterval:
                    CPLs.append(self.allCPLs[CPIndex])
                else:
                    # 初始化startTime，endTime，CPLs；递增TSId
                    endTime = startTime + timeInterval
                    timeSegment = TS(TSId=cntNgrid + 1, CPLs=CPLs, startTime=startTime, endTime=endTime)
                    self.TSS.append(timeSegment)
                    startTime = endTime
                    CPLs = []
                    CPIndex -= 1
                    previousIndexLs.append(CPIndex)
                    cntNgrid += 1
                CPIndex += 1
            else:
                cntNgrid = cntNgrid + 1
                endTime = self.timePtsLs[-1]
                CPLs = self.allCPLs[CPIndex:]
                timeSegment = TS(TSId=cntNgrid, CPLs=CPLs, startTime=startTime, endTime=endTime)
                self.TSS.append(timeSegment)
                break
        # 开始划分high TS set和 low TS set
        for TSData in self.TSS:
            CPdensity = len(TSData.CPLs)
            # print("CPdensity=", CPdensity)
            if CPdensity >= self.gt:
                self.HTSS.append(TSData)
            else:
                self.LTSS.append(TSData)
        # 开始合并相邻的高密度HTS
        mergeHTSLs = []
        findAdjacentHTS = self.getAdjacentHTS()
        for adjacentTS in findAdjacentHTS:
            index = 0
            mergeHTS = adjacentTS[0]
            while index < len(adjacentTS) - 1:
                mergeHTS = mergeHTS.merge(adjacentTS[index + 1])
                index += 1
            mergeHTSLs.append(mergeHTS)
        # 根据ADist将低密度LTS合并到最近的HTS中去
        mergeIndexLs = []
        for LTS in self.LTSS:
            if mergeHTSLs and LTS:
                minADist = LTS.ADist(mergeHTSLs[0])
                minIndex = 0
                # 找出与LST的元素中ADist最小的mergeHTSLs中的下标
                for index in range(1, len(mergeHTSLs)):
                    ADist_ij = LTS.ADist(mergeHTSLs[index])
                    if ADist_ij < minADist:
                        minADist = ADist_ij
                        minIndex = index
                mergeIndexLs.append(minIndex)
        # 开始找出重复合并的组成字典
        mergeLTSDict = dict()
        preMerge = mergeIndexLs[0]
        mergeLTSDict[preMerge] = []
        mergeLTSDict[preMerge].append(self.LTSS[0])
        for currentMergeIndex in range(1, len(mergeIndexLs)):
            currentMerge = mergeIndexLs[currentMergeIndex]
            if currentMerge == preMerge:
                mergeLTSDict[preMerge].append(self.LTSS[currentMergeIndex])
            else:
                mergeLTSDict[currentMerge] = []
                mergeLTSDict[currentMerge].append(self.LTSS[currentMergeIndex])
            preMerge = currentMerge
        # 开始合并
        for merge in mergeLTSDict.keys():
            LTS = mergeLTSDict[merge]
            mergeLTS = LTS[0]
            if len(LTS) >= 2:
                for LTSindex in range(len(LTS) - 1):
                    mergeLTS = mergeLTS.merge(LTS[LTSindex + 1])
                mergeLTS = mergeLTS.merge(mergeHTSLs[merge])
                self.ITSS.append(mergeLTS)
            else:
                mergeLTS = mergeLTS.merge(mergeHTSLs[merge])
                self.ITSS.append(mergeLTS)
        # 添加没合并的
        mergeofKeys = mergeLTSDict.keys()
        for index in range(len(mergeHTSLs)):
            if index not in mergeofKeys:
                self.ITSS.append(mergeHTSLs[index])
        # 按照开始时间排序
        self.ITSS.sort(key=lambda TSObj: TSObj.startTime)
        # self.ITSS.sort(key=lambda TSObj: TSObj.TSId)
        # 将timeStamp转换为date
        for ITS in self.ITSS:
            ITS.startDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ITS.startTime))
            ITS.endDate = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ITS.endTime))
        return self.ITSS
