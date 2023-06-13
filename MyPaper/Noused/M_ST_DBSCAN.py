# !/usr/bin/env python
# -*- coding: utf-8 -*-
from st_dbscan import ST_DBSCAN
import numpy as np
from BasicModule.Region import Region


class M_ST_DBSCAN:

    def __init__(self, allTrajectoryLs):
        self.allTrajectoryLs = allTrajectoryLs
        self.eps1 = 0.5  # spatial density threshold
        self.eps2 = 10  # temporal density threshold
        self.min_samples = 5
        self.metric = 'euclidean'
        self.n_jobs = -1
        # allTrajectoryLs转换为X
        self.X = np.array([])
        self.allPts = []
        self.significantPlacesLs = []

    # 方法1：设置参数
    def setAttribute(self,
                     eps1=0.5,
                     eps2=10,
                     min_samples=5,
                     metric='euclidean',
                     n_jobs=-1):
        self.eps1 = eps1  # spatial density threshold
        self.eps2 = eps2  # temporal density threshold
        self.min_samples = min_samples
        self.metric = metric
        self.n_jobs = n_jobs

    # 方法2: allTrajectoryLs转换为X
    def transferInput(self):
        X = []
        for trajectory in self.allTrajectoryLs:
            trajectoryPoints = trajectory.T
            for p in trajectoryPoints:
                X.append(np.array([p.timeStamp, p.latitude, p.longitude]))
                self.allPts.append(p)
        return np.array(X)

    # 方法3：开始聚类，获得Stopregion
    def getSignificantPlacesLs(self):
        X = self.transferInput()
        st_optics_obj = ST_DBSCAN(eps1=self.eps1, eps2=self.eps2, min_samples=self.min_samples)
        st_optics_result = st_optics_obj.fit(X)
        labels = st_optics_result.labels
        counts = np.max(labels)
        resultLs = []
        for i in range(counts):
            resultLs.append([])
        for i in range(len(labels)):
            label = labels[i]
            if label != -1:
                resultLs[label - 1].append(self.allPts[i])
        Rid = 1
        for SP in resultLs:
            stopRegion_obj = Region(Rid=Rid, region=SP)
            stopRegion_obj.setAttribute()
            self.significantPlacesLs.append(stopRegion_obj)
            Rid += 1
        print("SgnificantPlaces的总数", len(self.significantPlacesLs))
        return self.significantPlacesLs
