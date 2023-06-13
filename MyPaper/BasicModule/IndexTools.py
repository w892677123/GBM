# !/usr/bin/env python
# -*- coding: utf-8 -*-
from sklearn import metrics
from collections import Counter
#from s_dbw import S_Dbw


# index 指数；指标
# 轮廓系数： 高内聚(簇内紧凑)，低耦合（簇外分离） [-1 ，1]，越高越好

class IndexTools:  # 指标工具
    def __init__(self, allTrajectoryLs, significantPlacesLs):
        self.allTrajectoryLs = allTrajectoryLs  # 原始的所有轨迹组成的列表
        self.significantPlacesLs = significantPlacesLs  # 聚类结果组成的列表

    # 1 轮廓系数
    def get_silhouette(self):
        """
           某个样本s(i)的轮廓系数：s(i)=(b-a)/max(a, b), 其中a为s(i)与其所在簇内其他样本的平均距离(体现内聚度), b为
           s(i)与最近的簇样本中的点的平均距离(体现分离度)，簇内只有1点时,s(i)=0
           """
        allClusterPts = []  # 存储要算轮廓系数的所有样本点的经纬度
        labels = []
        scores = []  # 存储每个簇所有点的轮廓系数值的平均数
        cnt = 0
        # 将每个簇中的gps点的经纬度组成列表，加入stops，用cnt来区分这些点原来属于那些簇
        for SP_obj in self.significantPlacesLs:
            SP = SP_obj.region
            for gpsPoint in SP:
                allClusterPts.append([gpsPoint.latitude, gpsPoint.longitude])
                labels.append(cnt)
            cnt = cnt + 1
        # 计算所有样本的平均轮廓系数
        if len(labels) == 1 or len(labels) == 0:
            scoreAvg = 0
        else:
            scoreAvg = metrics.silhouette_score(allClusterPts, labels)
        # 计算每个样本点的轮廓系数值
        sample_silhouette_values = metrics.silhouette_samples(allClusterPts, labels)
        # 汇总属于簇i的样本的轮廓系数
        counterDict = Counter(labels)
        accumulateNum = 0
        for value in counterDict.values():
            lastIndex = accumulateNum + value
            ith_cluster_silhouette_values = sample_silhouette_values[accumulateNum:lastIndex]
            accumulateNum += value
            ithSize = ith_cluster_silhouette_values.size
            if ithSize:
                scores.append(sum(ith_cluster_silhouette_values) / ithSize)
            else:
                scores.append(0)
        return scoreAvg, scores

    '''
    # 2 S_Dbw有效性指数
    def get_S_Dbw(self):
        allClusterPts = []  # 存储要算轮廓系数的所有样本点的经纬度
        labels = []
        cnt = 0
        # 将每个簇中的gps点的经纬度组成列表，加入stops，用cnt来区分这些点原来属于那些簇
        for SP_obj in self.significantPlacesLs:
            SP = SP_obj.region
            for gpsPoint in SP:
                allClusterPts.append([gpsPoint.latitude, gpsPoint.longitude])
                labels.append(cnt)
            cnt = cnt + 1
        # 计算聚类结果的S_Dbw有效性指数的值
        if len(labels) == 1 or len(labels) == 0:
            scores = 0  # scores越小 -> 聚类结果越好
        else:
            scores = S_Dbw(allClusterPts, labels, centers_id=None, method='Tong', alg_noise='comb', centr='mean',
                           nearest_centr=True, metric='euclidean')
        return scores
    
    '''
