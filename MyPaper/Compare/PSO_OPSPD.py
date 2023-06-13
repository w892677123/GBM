# !/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import random
from sklearn.cluster import DBSCAN
from BasicModule.S_Dbw import S_Dbw
from BasicModule.Region import Region
import warnings


class PSO_OPSPD:

    def __init__(self, trajectoryLs):
        # spatial trajectory data:n*2, n is number of GPS, [longitude,latitude]
        # trajectoryLS是所有轨迹点的列表
        np.seterr(divide='ignore', invalid='ignore')
        warnings.filterwarnings("ignore")
        self.allTrajectoryLs = trajectoryLs
        self.S = []
        self.n = 0  # 轨迹点的数量
        self.E_lb = 5  # EPS的最小下界 the lower bound of EPS range
        self.E_ub = 10  # EPS的最大下界 the uper bound of EPS range
        self.m_lb = 2  # MinPts的最小下界 lower bound of Minimun points range(MinPts)
        self.m_ub = 5  # MinPts的最大上界 uper bound of Minimun points range(MinPts)
        self.N = 50  # 粒子的数量 Number of particle, 50或者100
        self.Particle = np.zeros([self.N, 2])  # Particle矩阵，存放[[EPS0, MinPts0], ..., [EPSN-1, MinPtsN-1]]
        self.Fitness0 = np.zeros(self.N)  # 存放S_Dbw的值的数组
        self.Fitness1 = np.zeros(self.N)
        # 文章建议的参数
        self.w_max = 0.9  # 最大惯性权重 the max inertial weight
        self.w_min = 0.4  # 最小惯性权重 the min inertial weight
        self.c1 = 2  # 认知系数 cognitive coefficient
        self.c2 = 2  # 社会系数 social coefficient
        self.MaxIeration = 100  # 最大迭代次数100
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

    # 方法1：设置阈值参数
    def setAttribute(self, N=50, MaxIeration=100, E_lb=5, E_ub=10, m_lb=2, m_ub=5):
        self.N = N
        self.MaxIeration = MaxIeration
        self.Particle = np.zeros([self.N, 2])
        self.Fitness0 = np.zeros(self.N)
        self.Fitness1 = np.zeros(self.N)
        self.E_lb = E_lb
        self.E_ub = E_ub
        self.m_lb = m_lb
        self.m_ub = m_ub
        self.transferInput()  # 转换得到S

    # 方法2: allTrajectoryLs转换为S
    def transferInput(self):
        X = []
        for trajectory in self.allTrajectoryLs:
            trajectoryPoints = trajectory.T
            for p in trajectoryPoints:
                # X.append(np.array([p.longitude, p.latitude]))
                X.append(np.array([p.x, p.y]))
                self.allPoints.append(p)
                self.S = np.array(X)
        self.n = self.S.shape[0]

    # 方法3：PSO核心方法，找出最合适的Gbest=[EPS, MinPts]
    def getGbest(self):
        # 1初始化粒子的位置
        for i in range(self.N):  # initialize the position of particles
            self.Particle[i, 0] = random.uniform(self.E_lb, self.E_ub)  # uniform(a, b)生成范围在[a, b]内的实数
            self.Particle[i, 1] = random.uniform(self.m_lb, self.m_ub)  # randint(a, b)生成[a, b]内的整数
        v = 0.1 * self.Particle  # 初始化速度initial velocity
        for i in range(self.N):
            db = DBSCAN(eps=self.Particle[i, 0], min_samples=self.Particle[i, 1]).fit(self.S)
            C = db.labels_
            S_Dbw_obj = S_Dbw(self.S, C)
            self.Fitness0[i] = S_Dbw_obj.result()
        a = np.argmin(self.Fitness0)
        Gbestvalue = self.Fitness0[a]  # 最小的S_Dbw值
        Pbest = self.Particle
        Gbest = self.Particle[a, :]  # 当达到最小的S_Dbw值的时候，最优的EPS值与MinPts值
        Iteration = 1
        # MaxIeration最大迭代次数，文中给的100
        while Iteration <= self.MaxIeration:
            w = self.w_max - (self.w_max - self.w_min) * Iteration / self.MaxIeration  # inertial weight update
            for i in range(self.N):  # 原文有误, n改成N
                r1 = random.random() + 0.000001  # [0, 1)的随机数
                r2 = random.random() + 0.000001
                for j in range(2):
                    v[i, j] = abs(w * v[i, j] + self.c1 * r1 * (Pbest[i, j] - self.Particle[i, j]) + self.c2 * r2 * (
                            Gbest[j] - self.Particle[i, j]))
            for i in range(self.N):
                for j in range(2):
                    self.Particle[i, j] = self.Particle[i, j] + v[i, j]
            # 计算Fitness1
            for i in range(self.N):
                db = DBSCAN(eps=self.Particle[i, 0], min_samples=self.Particle[i, 1]).fit(self.S)
                C = db.labels_
                S_Dbw_obj = S_Dbw(self.S, C)
                self.Fitness1[i] = S_Dbw_obj.result()
            for i in range(self.N):
                if self.Fitness1[i] < self.Fitness0[i]:
                    Pbest[i, :] = self.Particle[i, :]
                    self.Fitness0[i] = self.Fitness1[i]
            a = np.argmin(self.Fitness1)
            if Gbestvalue < self.Fitness1[a]:
                Gbestvalue = self.Fitness1[a]
                Gbest = self.Particle[a, :]
            Iteration = Iteration + 1
        return Gbest

    # 方法4：用得到的Gbest中的参数值进行聚类，获得重要地点
    def getSignificantPlacesLs(self):
        Gbest = self.getGbest()
        print("Gbest=", Gbest)
        db_result = DBSCAN(eps=Gbest[0], min_samples=Gbest[1]).fit(self.S)
        labels = db_result.labels_
        counts = np.max(labels)
        resultLs = []
        for i in range(counts):
            resultLs.append([])
        for i in range(len(labels)):
            label = labels[i]
            if label != -1:
                resultLs[label - 1].append(self.allPoints[i])
        Rid = 1
        for SP in resultLs:
            stopRegion_obj = Region(Rid=Rid, region=SP)
            stopRegion_obj.setAttribute()
            self.significantPlacesLs.append(stopRegion_obj)
            Rid += 1
        print("SgnificantPlaces的总数", len(self.significantPlacesLs))
        return self.significantPlacesLs
#  [[GPSPoint, ][]]
# self.allGpsPoints = [ gps1 gps2   ]
#  [0,1,2, ... , N-1].
#  [4,5,6,7,200,201]
# self.significantPlacesLs.append(self.allGpsPoints[4])
