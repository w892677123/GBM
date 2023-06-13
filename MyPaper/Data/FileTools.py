# !/usr/bin/env python
# -*- coding: utf-8 -*-
from BasicModule.Trajectory import Trajectory
from BasicModule.GPSPoint import GPSPoint
from BasicModule.Region import Region


class FileTools:
    def __init__(self, fileNumber):
        self.fileNumber = fileNumber  # 文件总数
        self.fileNameLs = []  # 文件名
        self.fileTsLs = []  # 读入的文件点结果, 尚未形成trajectory对象
        self.trajectoryLs = []  # 最终返回的轨迹对象列表, 已经形成trajectory对象
        self.originRegionLs = []  # 有初始标签的话返回初始标签形成的Stop
        self.realStop = []
        self.realMove = []

    # 方法1：读取文件
    def readFile(self, transfer=False):
        if transfer:
            self.transferInput()
        for i in range(1, self.fileNumber + 1):
            fileName = "Data\\data" + str(i) + ".txt"
            self.fileNameLs.append(fileName)
        Tid = 1
        for fileName in self.fileNameLs:
            with open(fileName, "r") as fp:
                dataLs = fp.readlines()
            totalPoints = []
            count = 0  # 统计点的数量，用来修正下标
            TIndex = 0  # 某条轨迹内部的下标
            # originStopRegion需要的变量
            Rid = 1  # 区域id
            finishAdd = False
            originStopRegionLs = []
            for data in dataLs:
                splitData = data.strip("\n").split("\t")
                if splitData is not None:
                    latitude = float(splitData[0])
                    longitude = float(splitData[1])
                    date = splitData[2]
                    gpsPoint = GPSPoint(Tid, TIndex, latitude, longitude, date)
                    # 注意：当类中的变量和方法同名时，对象.x调用的是方法，这样会引起混淆，故建议变量和方法不要同名
                    totalPoints.append(gpsPoint)
                    # 修正某些点的速度
                    if count >= 1:
                        gpsPoint.velocity = gpsPoint.insVelocity(totalPoints[count - 1])
                    if count >= 2:
                        totalPoints[count - 1].angle = totalPoints[count - 1].changingAngle(totalPoints[count - 2],
                                                                                            gpsPoint)
                    count += 1
                    TIndex += 1
                    # 计算originStopRegion
                    if len(splitData) >= 4:
                        label = splitData[3]
                        # gpsPoint.setLabel(trueLable=label)
                        # print("TIndex,Label=", (TIndex, label))
                        # 读取realStop和realMove
                        if label == 'MOVING':
                            self.realMove.append(gpsPoint)
                        else:
                            self.realStop.append(gpsPoint)
                        # ########
                        if label == 'MOVING' and originStopRegionLs and not finishAdd:
                            originStopRegionLs_obj = Region(Rid=Rid, region=originStopRegionLs)
                            originStopRegionLs_obj.setAttribute()
                            if originStopRegionLs_obj.duration >= 0:
                                self.originRegionLs.append(originStopRegionLs_obj)
                            originStopRegionLs = []
                            Rid += 1
                            finishAdd = True
                        if label == 'STOPPED':
                            originStopRegionLs.append(gpsPoint)
                            finishAdd = False
            # 补充第0个点的速度和角度(+0.0005近似修正)
            totalPoints[0].velocity = totalPoints[1].velocity + 0.0005
            totalPoints[0].angle = totalPoints[1].angle + 1
            totalPoints[-1].angle = totalPoints[-2].angle + 1
            self.fileTsLs.append(totalPoints)
            Tid += 1
        # 开始转换为trajectory对象
        for i in range(1, self.fileNumber + 1):
            trajectory = Trajectory(self.fileTsLs[i - 1], i)
            self.trajectoryLs.append(trajectory)
        return self.trajectoryLs

    # 转换输入文件的格式
    def transferInput(self):
        transferFileName = "Data\\transfer.txt"
        with open(transferFileName, "r") as fp:
            dataLs = fp.readlines()
        inputStr = ""
        for data in dataLs:
            splitData = data.strip("\n").replace(" ", "").split(",")
            if splitData is not None:
                latitude = round(float(splitData[1]), 6)
                longitude = round(float(splitData[2]), 6)
                date = splitData[3].replace("T", " ")[0:19]
                label = splitData[4]
                inputStr += str(latitude) + "\t" + str(longitude) + "\t" + str(date) + "\t" + label + "\n"
        inputStr = inputStr.strip("\n")  # 去掉最后的\n
        inputFileName = "Data\\data1.txt"
        with open(inputFileName, "w") as fp:
            fp.write(inputStr)

    def readOriginFile(self):
        totalPoints = []
        fileName = "Data\\data1.txt"
        with open(fileName, "r") as fp:
            dataLs = fp.readlines()
        TIndex = 0
        divisor = 1  # 控制加的点的数量
        for data in dataLs:
            splitData = data.strip("\n").split("\t")
            if splitData is not None:
                latitude = float(splitData[0])
                longitude = float(splitData[1])
                date = splitData[2]
                gpsPoint = GPSPoint(1, TIndex, latitude, longitude, date)
                if TIndex % divisor == 0:
                    totalPoints.append(gpsPoint)
                TIndex += 1
        self.fileTsLs.append(totalPoints)

    # 方法2:  检验算出来的速度和角度，写入文件，不检验时不用
    def writeFile(self):
        for trajectory in self.trajectoryLs:
            T = trajectory.T
            distance_str = ""
            angle_str = ""
            v_str = ""
            for i in range(1, len(T) - 2):
                distance_str = distance_str + str(T[i].distance(T[i + 1])) + "\n"
                angle_str = angle_str + str(T[i].angle) + "\n"
                v_str = v_str + str(T[i].velocity) + "\n"
            with open("Results\\Text\\" + str(trajectory.Tid) + "+ distance.txt", "w") as fp:
                fp.write(distance_str)
            with open("Results\\Text\\" + str(trajectory.Tid) + "+ angle.txt", "w") as fp:
                fp.write(angle_str)
            with open("Results\\Text\\" + str(trajectory.Tid) + "+ velocity.txt", "w") as fp:
                fp.write(v_str)
