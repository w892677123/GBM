import math


class MCC:
    def __init__(self, fileTsLs, forecastStop, realStop, realMoving):
        self.TP = 0
        self.FN = 0
        self.FP = 0
        self.TN = 0
        self.MCC = 0
        self.fileTsLs = fileTsLs
        self.forecastStop = forecastStop
        self.realStop = realStop
        self.realMoving = realMoving
        self.forecastMoving = []
        self.forecastMovingNumber = 0
        self.forecastStopNumber = len(forecastStop)
        self.realStopNumber = len(realStop)  # 702
        self.realMovingNumber = len(realMoving)  # 1068
        self.N = len(fileTsLs)
        self.forecastStop.sort(key=lambda stop: stop.timeStamp)  # 按时间戳排序
        sIndex = 0
        fIndex = 0
        while fIndex < self.N and sIndex < self.forecastStopNumber:
            if self.forecastStop[sIndex].timeStamp != self.fileTsLs[fIndex].timeStamp:
                self.forecastMoving.append(self.fileTsLs[fIndex])
            if self.forecastStop[sIndex].timeStamp == self.fileTsLs[fIndex].timeStamp:
                sIndex += 1
            fIndex += 1
        #
        while fIndex < self.N:
            self.forecastMoving.append(self.fileTsLs[fIndex])
            fIndex += 1
        self.forecastMovingNumber = len(self.forecastMoving)

    def ComputeMCC(self):
        # 计算TP
        fIndex = 0
        rIndex = 0
        while fIndex < self.forecastStopNumber and rIndex < self.realStopNumber:
            if self.forecastStop[fIndex].timeStamp < self.realStop[rIndex].timeStamp:
                fIndex += 1
            elif self.forecastStop[fIndex].timeStamp > self.realStop[rIndex].timeStamp:
                rIndex += 1
            else:
                self.TP += 1
                rIndex += 1
                fIndex += 1
        # 计算TN
        fIndex = 0
        rIndex = 0
        while fIndex < self.forecastMovingNumber and rIndex < self.realMovingNumber:
            if self.forecastMoving[fIndex].timeStamp < self.realMoving[rIndex].timeStamp:
                fIndex += 1
            elif self.forecastMoving[fIndex].timeStamp > self.realMoving[rIndex].timeStamp:
                rIndex += 1
            else:
                self.TN += 1
                rIndex += 1
                fIndex += 1
        # 计算FP
        fIndex = 0
        rIndex = 0
        while fIndex < self.forecastStopNumber and rIndex < self.realMovingNumber:
            if self.forecastStop[fIndex].timeStamp < self.realMoving[rIndex].timeStamp:
                fIndex += 1
            elif self.forecastStop[fIndex].timeStamp > self.realMoving[rIndex].timeStamp:
                rIndex += 1
            else:
                self.FP += 1
                rIndex += 1
                fIndex += 1
        # 计算FN
        fIndex = 0
        rIndex = 0
        while fIndex < self.forecastMovingNumber and rIndex < self.realStopNumber:
            if self.forecastMoving[fIndex].timeStamp < self.realStop[rIndex].timeStamp:
                fIndex += 1
            elif self.forecastMoving[fIndex].timeStamp > self.realStop[rIndex].timeStamp:
                rIndex += 1
            else:
                self.FN += 1
                rIndex += 1
                fIndex += 1
        print("TP:", self.TP, ",TN:", self.TN, ",FN:", self.FN, ",FP:", self.FP)
        scoreMcc = (self.TP * self.TN - self.FP * self.FN) / math.sqrt(
            (self.TP + self.FP) * (self.TP + self.FN) * (self.TN + self.FP) * (self.TN + self.FN))

        return scoreMcc
