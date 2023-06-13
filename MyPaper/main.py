# !/usr/bin/env python
# -*- coding: utf-8 -*-
import math
from time import *
from Data.FileTools import FileTools
# from Visualization.Map.GISPlot import GISPlot
from BasicModule.IndexTools import IndexTools
from Core.GB_SPM import GB_SPM
from Visualization.Drawing.PlotTools import PlotTools
from BasicModule.Region import Region
from BasicModule.MCC import MCC
from Compare.POSMIT import POSMIT

"""
# mNT的取值范围0.35-1, MD=0.08, samplingRates的值[0, 5]，取5，delta NMA = 0.5
# min-Stop=180s，min-move=300s，R=30, 50, 70
TAD_obj = TAD(trajectoryLs)
TAD_obj.setAttribute(min_Density=0.08, min_NT=0.5, min_Duration=18, min_Move=30, samplingRates=5)
# deltaNMA ="auto"意味着deltaNMA要综合所有NMA自己算; deltaNMA ="default"意味着deltaNMA=0.5
# SC = TAD_obj.TAD(R=50, deltaNMA="default")
# stopRegionLs = TAD_obj.getStopRegionLs(R=70, deltaNMA="default")
"""
"""
测试模块
flatNMASTLs, flatNTLs = TAD_obj.NMASTLs(R=50, deltaNMA="default")
print("NMAST", flatNMASTLs)
scatterPlot_obj.plotNMAST(flatNMASTLs)
"""
"""
    for SP in significantPlacesLs:
        print("点的数目, 半径, 时间", [SP.totalPoints, SP.R, SP.duration])
    print("Stops的个数为", len(significantPlacesLs))
"""
"""
ST_SPD_obj.setAttribute(ngrid=17, gt=5, R=30, vt=1, dct=20, tt=30, minSPTime=120, samplingRate=5, eps=30)
significantPlacesLs = ST_SPD_obj.getSignificantPlacesLs()
"""
"""  
将输入转换成ST-OPTICS需要的输入array([[0,0.45,0.43], [0,0.54,0.34],...])
"""
"""
STC_SMoT_obj = STC_SMoT(trajectoryLs)
STC_SMoT_obj.setAttribute(MinStopDur=6, samplingRates=1, SC=1.5, SR=50, MV=2, MaxStopDur=398)
significantPlacesLs = STC_SMoT_obj.getSignificantPlacesLs()
"""
"""
GB_SPD_obj = GB_SPD(trajectory)
GB_SPD_obj.setAttribute(R=10, vt=0.5, eps=7.5, hi=3)
ST_SPD_obj = ST_SPD(trajectoryLs)
ST_SPD_obj.setAttribute(ngrid=15, gt=5, R=10, vt=1, dct=20, tt=6, minSPTime=6, samplingRate=1, eps=7.5)
"""


def main():
    # 开始读取数据集
    readFile_obj, trajectoryLs = read_data(fileNumber=1)  # fileNumber = 1  # 单轨迹(只读一条轨迹)
    trajectory = trajectoryLs[0]  # 单轨迹只取第一条轨迹
    print("-------开始设置阈值参数-------")
    # 开始重要地点挖掘
    GB_SPM_obj = GB_SPM(trajectory)
    GB_SPM_obj.setAttribute(hi=1, vt=0.73)  # indexR=hi*3,故这里indexR=3,0.73
    significantPlacesLs = run(GB_SPM_obj)
    # 重新构造簇
    # SPIdxLs = get_idx(significantPlacesLs)
    # SPLs = create_region_from_idxLs(trajectory, SPIdxLs=SPIdxLs)
    # 开始计算轮廓系数

    # compute_SI(trajectoryLs, significantPlacesLs)
    # # 开始设置真实标签和预测标签
    # predict_stops = set_label(trajectory, significantPlacesLs)
    # # 开始计算MCC
    # compute_MCC(trajectory, predict_stops)
    # # 开始写入结果
    # write_ferry(trajectory, predict_stops)
    # # 开始画地图
    # # draw_map(readFile_obj, significantPlacesLs)


def run(obj):
    print("------开始重要地点挖掘-------")
    begin_t = time()
    significantPlacesLs = obj.getSignificantPlacesLs()
    end_t = time()
    print("总时间=", end_t - begin_t)
    print("-------重要地点挖掘完毕-------")
    for sp in significantPlacesLs:
        for pt in sp.region:
            pt.setLabel(predictLabel="Pre_Stop")
    # for SP in significantPlacesLs:
    #     print("点的数目, 半径, 时间", [SP.totalPoints, SP.R, SP.duration])
    print("结果Stops的个数为", len(significantPlacesLs))
    return significantPlacesLs


# 1、开始读取数据集
def read_data(fileNumber):
    print("-------开始读取数据集-------")
    readFile_obj = FileTools(fileNumber=fileNumber)
    trajectoryLs = readFile_obj.readFile(transfer=False)
    # 转换为trajectory时的列表
    print_origin_region(readFile_obj)  # 打印初始地点分布
    return readFile_obj, trajectoryLs


# 2、打印初始的地点分布
def print_origin_region(readFile_obj):
    originRegionLs = readFile_obj.originRegionLs  # 若数据有标签
    for SP in originRegionLs:
        print("点的数目, 半径, 时间", [SP.totalPoints, SP.R, SP.duration])
    print("初始Stops的个数为", len(originRegionLs))


# 3、设置真实标签和预测标签
def set_label(trajectory, significantPlacesLs):
    # 设置真实标签
    with open("Data\\data1.txt", "r") as fp:
        labelContentLs = fp.readlines()
    for i in range(len(trajectory.T)):
        label = labelContentLs[i].strip("\n").split("\t")[3]
        trajectory.T[i].setLabel(label)
    pre_stops = set()
    for sp in significantPlacesLs:
        for pt in sp.region:
            pre_stops.add(pt.TIndex)
    return pre_stops


# 4、写入Ferry数据集的结果,全部结果和错误判断的结果
def write_ferry(trajectory, pre_stops):
    # 开始写入测试结果
    print("-------开始写入测试结果------")
    writeLs = []
    writeRes = ""
    for pt in trajectory.T:
        strRes = str(pt.latitude) + "\t" + str(pt.longitude) + "\t" + str(pt.date) + "\t" + str(
            pt.velocity) + "\t" + str(pt.trueLabel) + "\t"
        if pt.TIndex in pre_stops and pt.trueLabel == "STOPPED":
            writeLs.append((pt.TIndex, strRes + "Pre_Stop\tTP\t√\n"))
        elif pt.TIndex in pre_stops and pt.trueLabel == "MOVING":
            writeLs.append((pt.TIndex, strRes + "Pre_Stop\tFP\t×\n"))
        elif pt.TIndex not in pre_stops and pt.trueLabel == "STOPPED":
            writeLs.append((pt.TIndex, strRes + "Pre_Move\tFN\t×\n"))
        elif pt.TIndex not in pre_stops and pt.trueLabel == "MOVING":
            writeLs.append((pt.TIndex, strRes + "Pre_Move\tTN\t√\n"))
    writeLs.sort(key=lambda item: item[0])
    wrongLs = []
    wrongRes = ""
    for write in writeLs:
        if write[1].strip().split("\t")[7] == "×":
            wrongLs.append(write)
            wrongRes += str(write[0] + 1) + "\t" + write[1]
        writeRes += write[1]
    with open("Results\\Text\\finalRes.txt", "w", encoding="UTF-8") as fp:
        fp.write(writeRes.strip())
    with open("Results\\Text\\wrongRes.txt", "w", encoding="UTF-8") as fp:
        fp.write(wrongRes.strip())
    print("-------写入测试结果完毕------")


# 5、计算MCC
def compute_MCC(trajectory, pre_stops):
    print("-------开始算MCC------")
    TP = FP = FN = TN = 0
    for pt in trajectory.T:
        if pt.TIndex in pre_stops and pt.trueLabel == "STOPPED":
            TP += 1
        elif pt.TIndex in pre_stops and pt.trueLabel == "MOVING":
            FP += 1
        elif pt.TIndex not in pre_stops and pt.trueLabel == "STOPPED":
            FN += 1
        elif pt.TIndex not in pre_stops and pt.trueLabel == "MOVING":
            TN += 1
    print("TP:", TP, ",TN:", TN, ",FN:", FN, ",FP:", FP)
    MCCscore = (TP * TN - FP * FN) / math.sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN))
    print("MCC=", MCCscore)


# 6、计算SI
def compute_SI(trajectoryLs, significantPlacesLs):
    print("-------开始算轮廓系数------")
    indexTools_obj = IndexTools(allTrajectoryLs=trajectoryLs, significantPlacesLs=significantPlacesLs)
    scoreAvg, scores = indexTools_obj.get_silhouette()
    print("轮廓系数=", scoreAvg)


# 7、画地图
def draw_map(readFile_obj, significantPlacesLs):
    pltFileName = "result1"
    fileTsLs = readFile_obj.fileTsLs  # 原始轨迹Ls，为未转换成trajectory时的初始轨迹Ls
    originRegionLs = readFile_obj.originRegionLs  # 若数据有标签
    print("-------开始画地图------")
    gisPlot_obj = GISPlot(rawTsLs=fileTsLs, originPlaceLs=originRegionLs, stopRegionLs=significantPlacesLs)
    gisPlot_obj.plotLabeledMap(fileName=pltFileName)
    print("-------画地图结束-------")


# 特殊方法

def get_idx(significantPlacesLs):
    SPIdxLs = []
    for sp in significantPlacesLs:
        tempIdxLs = []
        for pt in sp.region:
            tempIdxLs.append(pt.TIndex)
        SPIdxLs.append(tempIdxLs)
    return SPIdxLs


def create_region_from_idxLs(trajectory, SPIdxLs):
    """
    根据区域的下标生成新的区域对象stopRegion_obj,然后添加到
    SPLs中形成类似SignificantPlacesLs的结果,作为SI计算的参数
    合并的时候改变SPIdxLs,再调用这个方法就能
    """
    SPLs = []
    allPts = trajectory.T
    Rid = 1
    for region_idx in SPIdxLs:
        region = []
        for idx in region_idx:
            region.append(allPts[idx])
        stopRegion_obj = Region(Rid=Rid, region=region)
        stopRegion_obj.setAttribute()
        SPLs.append(stopRegion_obj)
        Rid += 1
    return SPLs


main()
