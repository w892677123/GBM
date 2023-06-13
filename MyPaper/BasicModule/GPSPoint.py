# !/usr/bin/env python
# -*- coding: utf-8 -*-
from math import sin, asin, cos, radians, fabs, sqrt, acos, tan, pi, degrees, log
from geopy.distance import geodesic
import time


class GPSPoint:
    EARTH_RADIUS = 6381372  # 地球半径

    """def __init__(self, latitude, longitude, timeStamp):
        self.timeStamp = timeStamp  # 轨迹点的时间戳
        self.latitude = latitude  # 轨迹点的纬度
        self.longitude = longitude  # 轨迹点的经度"""

    def __init__(self, Tid, TIndex, latitude, longitude, date):
        self.Tid = Tid
        self.TIndex = TIndex
        timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        self.date = date
        timeStamp = int(time.mktime(timeArray))
        self.timeStamp = timeStamp  # 轨迹点的时间戳
        self.latitude = latitude  # 轨迹点的纬度
        self.longitude = longitude  # 轨迹点的经度
        self.x, self.y = self.millerToXYY()
        # 轨迹点的速度
        self.velocity = 0
        # 轨迹点的方向改变角
        self.angle = 0
        # 标签
        self.trueLabel = None
        self.predictLabel = None

    # 设置标签
    def setLabel(self, trueLable=None, predictLabel=None):
        self.trueLabel = trueLable
        self.predictLabel = predictLabel

    def settimeStamp(self, timeStamp):
        self.timeStamp = timeStamp

    # 方法1：根据公式计算两点间的距离
    def computeDistance(self, gpsPoint):
        latitude_first = self.latitude
        longitude_first = self.longitude
        latitude_second = gpsPoint.latitude
        longitude_second = gpsPoint.longitude
        # 获取纬度和经度的弧度
        latitude_radian_first = radians(latitude_first)
        latitude_radian_second = radians(latitude_second)
        longitude_radian_first = radians(longitude_first)
        longitude_radian_second = radians(longitude_second)
        # 两点经度和纬度的弧度差
        latitude_radianDifference = fabs(latitude_radian_first - latitude_radian_second)
        longitude_radianDifference = fabs(longitude_radian_first - longitude_radian_second)
        # haversine值：求距离的中间结果
        haversine = sin(latitude_radianDifference / 2) ** 2 + cos(latitude_first) * cos(latitude_second) * sin(
            longitude_radianDifference) ** 2
        # 距离
        distance = 2 * self.EARTH_RADIUS * asin(sqrt(haversine))
        return distance

    # 方法2：调用geopy包中点方法计算两点间的距离(方法2，方法1，二选1，方法二更精准)
    def distance(self, gpsPoint):
        latitude_first = self.latitude
        longitude_first = self.longitude
        latitude_second = gpsPoint.latitude
        longitude_second = gpsPoint.longitude
        distance = abs(geodesic((latitude_first, longitude_first), (latitude_second, longitude_second)).m)
        return distance

    # 方法2.1： 暂时方法算距离
    def distanceTemp(self, gpsPoint):
        x = self.latitude - gpsPoint.latitude
        y = self.longitude - gpsPoint.longitude
        distance = sqrt(x ** 2 + y ** 2)
        return distance

    # 方法3：求两点间的平均速度, 来逼近某点的瞬时速度
    def insVelocity(self, gpsPoint):
        velocity = 0
        distance = self.distance(gpsPoint)
        duration = abs(self.timeStamp - gpsPoint.timeStamp)
        if duration != 0:
            velocity = distance / duration
        return velocity

    # 方法4：将经纬度转换为平面坐标系的x，y
    def millerToXYY(self):
        L = self.EARTH_RADIUS * pi * 2
        W = L
        H = L / 2
        mill = 2.3
        x = self.longitude * pi / 180
        y = self.latitude * pi / 180
        y = 1.25 * log(tan(0.25 * pi + 0.4 * y))
        x = (W / 2) + (W / (2 * pi)) * x
        y = (H / 2) - (H / (2 * mill)) * y
        return x, y

    # 方法5：余弦公式求点的改变角
    def changingAngle(self, pBefore, pAfter):
        B = 0.0
        # 通过三点是否构成三角形判断三点是否共线
        triArea = pBefore.x * self.y - self.x * pBefore.y + self.x * pAfter.y - pAfter.x * self.y + pAfter.x * pBefore.y - pAfter.y * pAfter.x
        if triArea != 0.0:
            a = sqrt((self.x - pAfter.x) * (self.x - pAfter.x) + (self.y - pAfter.y) * (
                    self.y - pAfter.y))
            b = sqrt((pBefore.x - pAfter.x) * (pBefore.x - pAfter.x) + (pBefore.y - pAfter.y) * (
                    pBefore.y - pAfter.y))
            c = sqrt((pBefore.x - self.x) * (pBefore.x - self.x) + (pBefore.y - self.y) * (
                    pBefore.y - self.y))
            if a * c != 0.0:
                thetaV = (b * b - a * a - c * c) / (-2 * a * c)
                if abs(thetaV) <= 1:
                    B = degrees(acos(thetaV))
                else:
                    B = 0
        return B

    # 方法6：直接根据经纬度求夹角(未实现，采用的是将经纬度转化为x，y来求角，即方法4和方法5)
    def Aangle(self, pBefore, pAfter):
        pass

    # 设置插补点的时间戳
    def set_timeStamp(self, timeStamp):
        self.timeStamp = timeStamp
