# !/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from math import sqrt


class Trajectory:
    # 用户预设参数
    def __init__(self, T, Tid):
        self.T = T
        self.Tid = Tid
        self.N = len(self.T)
        self.u = 0
        self.sigma = 0
        self.variation = []  # 角度改变
        self.differentiation = []  # 速度改变

    # 方法1：算距离
    # 方法1.1：算轨迹段的直线距离的方法，pi为第一个点的下标，pj为最后一个点的下标
    def directDistance(self, pn, pm):
        GpsPoint_n = self.T[pn]
        GpsPoint_m = self.T[pm]
        directDistance = GpsPoint_n.distance(GpsPoint_m)
        return directDistance

    # 方法1.2：算轨迹段的曲线距离的方法，pi为第一个点的下标，pj为最后一个点的下标

    def curveDistance(self, pn, pm):
        curveDistance = 0
        if pn < pm:
            while pn < pm:
                curveDistance = curveDistance + self.T[pn].distance(self.T[pn + 1])
                pn = pn + 1
        else:
            while pm < pn:
                curveDistance = curveDistance + self.T[pm].distance(self.T[pm + 1])
                pm = pm + 1
        return curveDistance

    # 方法2：算轨迹段的移动能力MA
    # 方法2.1: 通过1.1和1.2算轨迹段移动能力的方法(全局移动能力)

    def movingAbility(self, pn, pm):
        Ddis = self.directDistance(pn, pm)
        Cdis = self.curveDistance(pn, pm)
        MA = 0
        if Cdis != 0:
            MA = Ddis / Cdis
        return MA

    # 方法3：ST-SPD需要用到的方法
    # 方法3.1：算轨迹段的时间, pi为第一个点的下标，pj为最后一个点的下标
    def TSDuration(self, pn, pm):
        GpsPoint_n = self.T[pn]
        GpsPoint_m = self.T[pm]
        duration = abs(GpsPoint_n.timeStamp - GpsPoint_m.timeStamp)
        return duration

    # 方法3.2：算轨迹段的速度
    def TSvelocity(self, pn, pm):
        curveDis = self.curveDistance(pn, pm)
        duration = self.TSDuration(pn, pm)
        if duration != 0:
            velocity = curveDis / duration
        else:
            velocity = (self.T[pn].velocity + self.T[pm].velocity) / 2
        if velocity >= 17:
            velocity = -0.1
        # if velocity >= 6:
        #     print("velocity=", velocity)
        #     print("pn, pm", pn, pm)
        #     print("Dis, duration", curveDis, duration)
        return velocity

    # 方法4：SMoTAS需要用到的方法
    # 方法4.1：求GPS点集中的距离均值u
    def setU(self):
        totalDistance = 0.0
        for i in range(self.N - 1):
            totalDistance = totalDistance + self.T[i].distance(self.T[i + 1])
        self.u = totalDistance / (self.N - 1)

    # 方法4.2：求GPS点集中的距离标准差sigma
    def setSigma(self):
        totalSquare = 0.0
        for i in range(self.N - 1):
            totalSquare = totalSquare + (self.T[i].distance(self.T[i + 1]) - self.u) ** 2
        self.sigma = sqrt(totalSquare / (self.N - 1))

    # 方法4.3: 求erf-1(x)
    def erf(self, x):
        N = 2500
        if N > 2500:
            N = self.N
        # 按照论文中的公式计算Ck
        C = [0] * N
        C[0] = 1
        for k in range(1, N):  # 1到400
            C[k] = 0
            for m in range(k):
                C[k] = C[k] + (C[m] * C[k - 1 - m]) / ((m + 1) * (2 * m + 1))
        # 按照论文中的公式计算erf-1(x)
        erf = 0.0
        for k in range(N):
            erf = erf + (C[k] / (2 * k + 1)) * ((sqrt(math.pi) * x / 2) ** (2 * k + 1))
        return erf

    # 方法4.4：通过高斯分布求F-1(q,u,sigma)
    def F_q_u_sigma(self, q, u, sigma):
        erf = self.erf(2 * q - 1)
        F = u + sigma * sqrt(2) * erf
        return abs(F)

    # 方法4.5：求点pi的领域（这个方法还会被其他方法调用）
    def Neibor(self, pi, neighbor):
        N_pi = [pi]
        # 找点pi左边的领域
        pk = pi
        if pk - 1 >= 0:
            distance = self.Dist(pk - 1, pk)
            while distance <= neighbor:
                N_pi.append(pk - 1)
                pk = pk - 1
                if pk - 1 >= 0:
                    distance = distance + self.Dist(pk - 1, pk)
                else:
                    break  # 防止因距离不够而导致无限循环
        # 找pi右边的eps领域
        pk = pi
        if pk + 1 <= self.N - 1:
            distance = self.Dist(pk, pk + 1)
            while distance <= neighbor:
                N_pi.append(pk + 1)
                pk = pk + 1
                if pk + 1 <= self.N - 1:
                    distance = distance + self.Dist(pk, pk + 1)
                else:
                    break  # 防止因距离不够而导致无限循环
        # print("N_pi=", N_pi)
        return N_pi

    # 方法4.6：获得速度和方向变化列表
    def setVariationDifferentiation(self):
        # 列表用list[i]赋值是需要指定大小，否则空列表无大小，会报下标越界错误
        self.variation.append(abs(self.T[1].angle - self.T[0].angle) + 1)
        self.differentiation.append(abs(self.T[1].velocity - self.T[0].velocity) + 1)
        for i in range(1, self.N):
            self.variation.append(abs(self.T[i].angle - self.T[i - 1].angle))
            self.differentiation.append(abs(self.T[i].velocity - self.T[i - 1].velocity))

    # 方法4.7：求轨迹中任意连续段的距离
    def Dist(self, pn, pm):
        distance = 0
        if pn < pm:
            while pn < pm:
                distance = distance + self.T[pn].distance(self.T[pn + 1])
                pn = pn + 1
        else:
            while pm < pn:
                distance = distance + self.T[pm].distance(self.T[pm + 1])
                pm = pm + 1
        return distance
