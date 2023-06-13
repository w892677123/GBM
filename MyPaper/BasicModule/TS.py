# !/usr/bin/env python
# -*- coding: utf-8 -*-


class TS:
    # TS：Time Segment
    def __init__(self, TSId, CPLs, startTime, endTime):
        self.CPLs = CPLs  # 特征点的列表
        # Time Segment自己的属性
        self.TSId = TSId  # 时间段的id
        self.startTime = startTime  # 时间段的开始时间
        self.endTime = endTime  # 时间段的结束时间
        self.startDate = ""
        self.endDate = ""
        self.startIndex = self.TSId
        self.endIndex = self.TSId

    # 方法1：算抽象距离ADist(TSi,TSj)
    def ADist(self, TSj):
        TSIdi = self.TSId
        startIndexj = TSj.startIndex
        endIndexj = TSj.endIndex
        ADistResult = min(abs(TSIdi - startIndexj), abs(TSIdi - endIndexj))
        return ADistResult

    # 方法2：合并TS，并返回合并后的对象
    def merge(self, TSj):
        mergeTS = TS(0, [], 0, 0)
        mergeTS.TSId = min(self.TSId, TSj.TSId)
        mergeTS.startTime = min(self.startTime, TSj.startTime)
        mergeTS.endTime = max(self.endTime, TSj.endTime)
        mergeTS.startIndex = min(self.startIndex, TSj.startIndex)
        mergeTS.endIndex = max(self.endIndex, TSj.endIndex)
        # mergeTS.CPLs = (self.CPLs + TSj.CPLs).sort(key=lambda CP: CP.timeStamp)
        mergeTS.CPLs = self.CPLs + TSj.CPLs
        return mergeTS
