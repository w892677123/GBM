# !/usr/bin/env python
# -*- coding: utf-8 -*-
from BasicModule.GPSPoint import GPSPoint
import math


class Region:

    def __init__(self, Rid, region):
        self.region = region
        self.Rid = Rid  # 这里从id改成的Rid
        self.latitude = 0
        self.longitude = 0
        self.startTime = 0
        self.totalPoints = len(self.region)
        self.duration = 0
        self.speed = 0
        self.centerPt = 0
        self.R = 0

    # 设置区域的各种属性
    def setAttribute(self):
        self.startTime = min(self.region, key=lambda point: point.timeStamp).timeStamp
        endTime = max(self.region, key=lambda point: point.timeStamp).timeStamp
        self.duration = endTime - self.startTime
        latitude = 0
        longitude = 0
        for i in range(self.totalPoints):
            self.speed = self.speed + self.region[i].velocity
            latitude = latitude + self.region[i].latitude
            longitude = longitude + self.region[i].longitude
        self.speed = self.speed / self.totalPoints
        self.latitude = round((latitude / self.totalPoints), 6)
        self.longitude = round((longitude / self.totalPoints), 6)
        # 找区域半径
        self.centerPt = GPSPoint(Tid=0, TIndex=0, latitude=self.latitude, longitude=self.longitude,
                                 date="2000-01-01   00:00:00")
        R = self.centerPt.distance(self.region[0])
        for ptIndex in range(1, self.totalPoints):
            currentR = self.centerPt.distance(self.region[ptIndex])
            if currentR > R:
                R = currentR
        self.R = math.ceil(R)
        # print("R, self.R", (R, self.R))
        # print("longitude, latitude", self.longitude, self.latitude)
