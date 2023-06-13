from BasicModule.GPSPoint import GPSPoint
from BasicModule.Region import Region
import math
import random


class STC_SMoT:

    def __init__(self, trajectoryLs):
        self.eps = 0
        self.N = 0  # 所有点的总数
        self.D = trajectoryLs  # 即D, 所有轨迹的列表
        self.numOfEachTra = []  # D中每条轨迹点的总数
        self.allPoints = []  # 所有轨迹的GPS点组成的列表
        self.stopRegionLs = []  # 存放最终停止区域的列表
        self.significantPlacesLs = []
        self.samplingRates = 0
        # 计算所有点的总数，将D拍平
        for trajectory in self.D:
            trajectoryLs = trajectory.T
            self.allPoints += trajectoryLs
            number = len(trajectoryLs)
            self.numOfEachTra.append(number)
            self.N += number

    def setAttribute(self, MinStopDur, samplingRates, SC, SR, MV, MaxStopDur):
        self.eps = samplingRates * SC  # SC是表示Eps和Interval之间关系的常数
        self.samplingRates = samplingRates
        self.MinStopDur = MinStopDur
        self.SR = SR  # gap距离的分界值
        self.MV = MV  # gap速度的分界值
        self.MaxStopDur = MaxStopDur

    # 插补时的处理，在temp后进行插补
    def point_imputation(self, trajectory, Tid, i, temp, timeStamp, volecity_x, volecity_y):
        # 插补的点的经纬度、时间戳、下标
        lat = trajectory.T[i].latitude + (
                trajectory.T[temp].timeStamp - trajectory.T[i].timeStamp + self.samplingRates) * volecity_x
        long = trajectory.T[i].longitude + (
                trajectory.T[temp].timeStamp - trajectory.T[i].timeStamp + self.samplingRates) * volecity_y

        index = temp + 1
        date = trajectory.T[temp].date  # 暂令插补点的date为前一个点的date
        # print("插补前一个点的时间为",date)
        # print("插补速度为",volecity_x,volecity_y)
        point_obj = GPSPoint(Tid=Tid, TIndex=index, latitude=lat, longitude=long, date=date)  # 生成插补点
        point_obj.set_timeStamp(timeStamp)  # 更新插补点的时间戳

        trajectory.T.insert(index, point_obj)  # 轨迹中插入插补点

        # print("插补点的纬度为",point_obj.latitude)
        point_obj.velocity = point_obj.insVelocity(trajectory.T[index - 1])  # 计算插补点的速度
        point_obj.angle = point_obj.changingAngle(trajectory.T[index - 1], trajectory.T[index + 1])  # 计算插补点的角度
        trajectory.N += 1
        self.N += 1
        return timeStamp + self.samplingRates

    # 轨迹插补算法

    def gap_imputation(self, trajectory, Tid, SR, MV, MinStopDur, MaxStopDur):
        stop = []
        move = []
        unvisited = [x for x in range(trajectory.N)]
        while len(unvisited) > 0:
            i = random.choice(list(unvisited))
            j = i + 1
            points_j = (trajectory.T[j])
            point_i = (trajectory.T[i])
            while ((points_j.timeStamp - point_i.timeStamp) <= MinStopDur) and j < trajectory.N - 1:  # 找与i点满足MinStopDur和MaxStopDur间隔的j点
                j += 1
                points_j = (trajectory.T[j])
            distance = trajectory.directDistance(i, j)
            volecity = distance / trajectory.TSDuration(i, j)
            # gap为Stop时
            if distance <= SR and volecity < MV:
                for x in range(i, j):
                    stop.append(x)
                    if x in unvisited:
                        unvisited.remove(x)
            # gap为Move时
            elif distance > SR and volecity >= MV:
                temp = i
                temp_next = i + 1
                while ((trajectory.T[temp_next]).timeStamp <= (trajectory.T[j]).timeStamp) and j < trajectory.N - 1:
                    if (trajectory.T[temp_next]).timeStamp <= (trajectory.T[temp]).timeStamp + self.samplingRates:
                        temp += 1
                        temp_next += 1
                    else:  # 需要进行插补
                        dur = trajectory.T[j].timeStamp - trajectory.T[i].timeStamp
                        v_x = (trajectory.T[j].latitude - trajectory.T[i].latitude) / dur
                        v_y = (trajectory.T[j].longitude - trajectory.T[i].longitude) / dur
                        self.point_imputation(trajectory, Tid, i, temp,
                                              trajectory.T[temp].timeStamp + self.samplingRates, v_x, v_y)
                        for x in unvisited:
                            if x > temp + 1:
                                x += 1
                        temp += 1
                        temp_next += 1
                        j += 1
                        # print("MOVE里进行插补，此时轨迹数为",trajectory.N)
                for x in range(i, j):
                    move.append(x)
                    if x in unvisited:
                        unvisited.remove(x)
            # gap为SAM时
            elif distance > SR and volecity < MV:
                temp = i
                temp_next = i + 1
                v_j = trajectory.T[j + 1].velocity
                # gap为Stop-Move时
                if volecity < v_j:
                    time_a = trajectory.T[j].timeStamp - distance / v_j
                    time_j = trajectory.T[j].timeStamp
                    while (trajectory.T[temp_next].timeStamp <= trajectory.T[j].timeStamp) and j < trajectory.N - 1:
                        if (trajectory.T[temp_next].timeStamp - trajectory.T[temp].timeStamp) <= self.samplingRates:
                            temp += 1
                            temp_next += 1
                        else:
                            if (j + 1) in move:
                                time_temp = trajectory.T[temp].timeStamp
                                if (time_temp + self.samplingRates) < time_a:
                                    time_temp += self.samplingRates
                                else:
                                    while (time_temp + self.samplingRates) >= time_a and (
                                            time_temp + self.samplingRates) <= trajectory.T[temp_next].timeStamp:
                                        # 需要进行插补trajectory, Tid, i, temp, timeStamp,volecity_x, volecity_y):
                                        d = trajectory.T[j + 1].timeStamp - trajectory.T[j].timeStamp
                                        v_x = (trajectory.T[j + 1].latitude - trajectory.T[j].latitude) / d
                                        v_y = (trajectory.T[j + 1].longitude - trajectory.T[j].longitude) / d
                                        time_temp = self.point_imputation(trajectory, Tid, i, temp,
                                                                          time_temp + self.samplingRates, v_x, v_y)
                                        j += 1
                                        for x in unvisited:
                                            if x > temp:
                                                x += 1
                                        # print("Stop-Move里第一种情况进行插补，此时轨迹数为", trajectory.N)
                                    j += 1
                                temp += 1
                                temp_next += 1

                            else:
                                time_temp = trajectory.T[temp].timeStamp
                                if (time_temp + self.samplingRates) < time_a:
                                    time_temp += self.samplingRates
                                else:
                                    d = trajectory.T[j].timeStamp - trajectory.T[i].timeStamp
                                    distance_x = 0
                                    distance_y = 0
                                    for y in range(i, j):
                                        distance_x += abs(trajectory.T[y + 1].latitude - trajectory.T[y].latitude)
                                        distance_y += abs(trajectory.T[y + 1].longitude - trajectory.T[y].longitude)
                                    flag_x = 1
                                    flag_y = 1
                                    if (trajectory.T[j].latitude - trajectory.T[i].latitude) < 0:
                                        flag_x = -1
                                    if (trajectory.T[j].longitude - trajectory.T[i].longitude) < 0:
                                        flag_y = -1
                                    v_x = flag_x * distance_x / d
                                    v_y = flag_y * distance_y / d
                                    time_temp = trajectory.T[temp_next].timeStamp
                                    while (time_temp + self.samplingRates) >= time_a and (
                                            time_temp + self.samplingRates) < trajectory.T[temp_next].timeStamp:

                                        # print("速度为", v_x, v_y)
                                        time_temp = self.point_imputation(trajectory, Tid, i, temp,
                                                                          time_temp + self.samplingRates, v_x, v_y)
                                        for x in unvisited:
                                            if x > temp + 1:
                                                x += 1
                                        # print("下个点的时间为", trajectory.T[temp_next].timeStamp)
                                        # print("Stop-MOVE里第二种情况进行插补，此时轨迹数为", trajectory.N)
                                    j += 1
                                temp += 1
                                temp_next += 1
                    for x in range(i, j):
                        if trajectory.T[x].timeStamp <= time_a:
                            stop.append(x)
                        else:
                            move.append(x)
                        if x in unvisited:
                            unvisited.remove(x)
                # gap为Move-Stop时
                else:
                    vbefore_i = trajectory.T[i - 1].velocity
                    if vbefore_i == 0:
                        vbefore_i = trajectory.T[i - 2].velocity
                    time_a = trajectory.T[i].timeStamp + distance / vbefore_i
                    # print("time_a是",time_a)
                    while (trajectory.T[temp_next].timeStamp <= trajectory.T[j].timeStamp) and j < trajectory.N - 1:
                        if (trajectory.T[temp_next].timeStamp - trajectory.T[temp].timeStamp) <= self.samplingRates:
                            temp += 1
                            temp_next += 1
                        else:
                            # time_a = trajectory.T[i].timeStamp + distance / vbefore_i
                            if (i - 1) in move:
                                time_temp = trajectory.T[temp].timeStamp
                                d = trajectory.T[i].timeStamp - trajectory.T[i - 1].timeStamp
                                v_x = (trajectory.T[i].latitude - trajectory.T[i - 1].latitude) / d
                                v_y = (trajectory.T[i].longitude - trajectory.T[i - 1].longitude) / d
                                while (time_temp + self.samplingRates) < time_a:
                                    time_temp = self.point_imputation(trajectory, Tid, i, temp,
                                                                      time_temp + self.samplingRates, v_x, v_y)
                                    # print("time_temp是：",time_temp)
                                    for x in unvisited:
                                        if (x > temp + 1):
                                            x += 1
                                    # print("MOVE-stop里第一种进行插补，此时轨迹数为", trajectory.N)
                                    j += 1
                                temp += 1
                                temp_next += 1
                            else:
                                d = trajectory.T[j].timeStamp - trajectory.T[i].timeStamp
                                distance_x = 0
                                distance_y = 0
                                for y in range(i, j):
                                    distance_x += abs(
                                        trajectory.T[y + 1].latitude - trajectory.T[y].latitude)
                                    distance_y += abs(
                                        trajectory.T[y + 1].longitude - trajectory.T[y].longitude)
                                flag_x = 1
                                flag_y = 1
                                if (trajectory.T[j].latitude - trajectory.T[i].latitude) < 0:
                                    flag_x = -1
                                if (trajectory.T[j].longitude - trajectory.T[i].longitude) < 0:
                                    flag_y = -1
                                v_x = flag_x * distance_x / d
                                v_y = flag_y * distance_y / d
                                time_temp = trajectory.T[temp].timeStamp
                                # print("time_a是：",time_a)
                                # print("time_temp是",time_temp)
                                while (time_temp + self.samplingRates) < time_a:
                                    time_temp = self.point_imputation(trajectory, Tid, i, temp,
                                                                      time_temp + self.samplingRates, v_x, v_y)
                                    # print("time_temp是", time_temp)
                                    for x in unvisited:
                                        if (x > temp + 1):
                                            x += 1
                                    # print("MOVE-stop里进行第二种插补，此时轨迹数为", trajectory.N)
                                    j += 1
                                temp += 1
                                temp_next += 1
                    for x in range(i, j):
                        if (trajectory.T[x].timeStamp) <= time_a:
                            move.append(x)
                        else:
                            stop.append(x)
                        if x in unvisited:
                            unvisited.remove(x)
            # gap为SOM时
            else:
                temp = i
                temp_next = i + 1
                time_temp = trajectory.T[temp].timeStamp
                if (i - 1) in stop and (j + 1) in stop:
                    for x in range(i, j + 1):
                        stop.append(x)
                        if x in unvisited:
                            unvisited.remove(x)
                else:
                    while (trajectory.T[temp_next].timeStamp <= trajectory.T[j].timeStamp) and (j < trajectory.N - 1):
                        if (trajectory.T[temp_next].timeStamp - trajectory.T[temp].timeStamp) <= self.samplingRates:
                            temp += 1
                            temp_next += 1
                        else:  # 需要进行插补
                            dur = trajectory.T[j].timeStamp - trajectory.T[i].timeStamp
                            v_x = (trajectory.T[j].latitude - trajectory.T[i].latitude) / dur
                            v_y = (trajectory.T[j].longitude - trajectory.T[i].longitude) / dur
                            self.point_imputation(trajectory, Tid, i, temp, time_temp + self.samplingRates, v_x, v_y)
                            for x in unvisited:
                                if x > temp + 1:
                                    x += 1
                            j += 1
                            temp += 1
                            temp_next += 1
                            # unvisited.append(trajectory.N)
                            # print("对SOM里的MOVE进行插补，此时轨迹数为", trajectory.N)
                    for x in range(i, j):
                        move.append(x)
                        if x in unvisited:
                            unvisited.remove(x)

    # 找点pi的spatio_temporal neighbor
    def N_RELN(self, trajectory, pi):
        STN_pi = [pi]
        # 找点pi左边的eps邻域
        pk = pi
        trajectoryPoints = trajectory.T
        if pk - 1 >= 0:
            # distance = pk.distance(trajectoryPoints[pk-1])
            distance = trajectoryPoints[pk].distance(trajectoryPoints[pk - 1])
            while distance <= self.eps:
                STN_pi.append(pk - 1)
                pk = pk - 1
                if pk - 1 >= 0:
                    distance = distance + trajectoryPoints[pk].distance(trajectoryPoints[pk - 1])
                else:
                    break
        # 找pi右边的eps邻域
        pk = pi
        if pk + 1 <= trajectory.N - 1:
            distance = trajectoryPoints[pk].distance(trajectoryPoints[pk + 1])
            while distance <= self.eps:
                STN_pi.append(pk + 1)
                pk = pk + 1
                if pk + 1 <= trajectory.N - 1:
                    distance = distance + trajectoryPoints[pk].distance(trajectoryPoints[pk + 1])
                else:
                    break
        return STN_pi

    def isCorePoint(self, trajectory, Neighbors):
        points = []
        neighborsDuration = 0
        for i in Neighbors:
            points.append(trajectory.T[i])
        if points:
            maxTime = max(points, key=lambda point: point.timeStamp).timeStamp
            minTime = min(points, key=lambda point: point.timeStamp).timeStamp
            neighborsDuration = maxTime - minTime
        if neighborsDuration >= self.MinStopDur:
            return True
        else:
            return False

    # STC-SMoT划分出Stop基段
    def STC_SMoT(self, trajectory):
        traj_stop = []
        visited = []
        unvisited = [x for x in range(trajectory.N)]
        # trajectoryPoints = trajectory.T
        while len(unvisited) > 0:
            pi = random.choice(list(unvisited))
            visited.append(pi)
            unvisited.remove(pi)
            STN_Pi = self.N_RELN(trajectory, pi)
            Cluster_C = []
            if self.isCorePoint(trajectory, STN_Pi):
                Cluster_C.append(pi)
                for pk in STN_Pi:
                    if pk in unvisited:
                        STN_Pk = self.N_RELN(trajectory, pk)
                        if self.isCorePoint(trajectory, STN_Pk):
                            Cluster_C.append(pk)
                        visited.append(pk)
                        unvisited.remove(pk)
            if Cluster_C:
                Cluster_C.sort()
                traj_stop.append(Cluster_C)
        # 排序
        if traj_stop:
            traj_stop.sort(key=lambda x: min(x))
        traj_move = self.getMovingRegion(trajectory, traj_stop)
        print("traj_stop是", traj_stop)
        print(len(traj_stop))
        return traj_stop, traj_move

    # 获取Move基段，用于模糊推理
    def getMovingRegion(self, trajectory, S_stop):
        S_moving = []
        if S_stop:
            S_stop.sort(key=lambda x: min(x))
            for i in range(1, len(S_stop)):
                movingPoints = []
                maxIndex = max(S_stop[i - 1])
                minIndex = min(S_stop[i])
                for j in range(maxIndex + 1, minIndex):
                    movingPoints.append(j)
                if movingPoints:
                    S_moving.append(movingPoints)
            if min(S_stop[0]) != 0:
                movingPoints = []
                for j in range(min(S_stop[0])):
                    movingPoints.append(j)
                if movingPoints:
                    S_moving.append(movingPoints)
            if max(S_stop[-1]) != trajectory.N - 1:
                movingPoints = []
                for j in range(max(S_stop[-1]), trajectory.N):
                    movingPoints.append(j)
                if movingPoints:
                    S_moving.append(movingPoints)
        else:
            S_moving = [x for x in range(trajectory.N)]
        if S_moving and isinstance(S_moving[0], list):
            S_moving.sort(key=lambda x: min(x))
        return S_moving

    # 模糊推理估计Stop和Move基段上的状态
    def fuzzy_inference(self):
        for trajectory in self.D:
            stop, move = self.STC_SMoT(trajectory)
            final_stop = []
            angle = 0
            speed = 0
            clusters = stop + move
            clusters.sort(key=lambda x: min(x))
            for S in clusters:
                N = len(S)
                for point in S:
                    angle += trajectory.T[point].angle
                    speed += trajectory.T[point].velocity
                if (N > 1 and trajectory.curveDistance(S[0], S[N - 1]) > 0):
                    circuity = trajectory.directDistance(S[0], S[N - 1]) / trajectory.curveDistance(S[0], S[
                        N - 1])  ####################################为什么还出现为0的情况
                else:
                    circuity = 1
                angle /= N
                speed /= N
                # print("直接距离与曲线总距离为", trajectory.directDistance(S[0], S[N - 1]),trajectory.curveDistance(S[0], S[N - 1]))
                s_stop = 1 / (1 + math.exp(2 * (speed - 1.2)))
                s_move = 1 / (1 + math.exp(-3 * (speed - 0.8)))
                a_stop = 1 / (1 + math.exp((angle - 95) / 8))
                a_move = 1 / (1 + math.exp(-(angle - 105) / 8))
                c_stop = 1 / (1 + math.exp(-2 * (circuity - 4)))
                c_move = 1 / (1 + math.exp(3 * (circuity - 2)))
                # print("s_stop,a_stop,c_stop分别是", s_stop, a_stop, c_stop)
                # print("s_move,a_move,c_move分别是", s_move, a_move, c_move)
                if ((s_stop + a_stop + c_stop) > (s_move + a_move + c_move)):
                    final_stop.append(S)
        return final_stop

    def getSignificantPlacesLs(self):
        for trajectory in self.D:
            self.gap_imputation(trajectory, trajectory.Tid, self.SR, self.MV, self.MinStopDur, self.MaxStopDur)
        print("插补完成")
        Stop = self.fuzzy_inference()
        print("STop=", Stop)
        print("Stop总数为", len(Stop))
        self.stopRegionLs = []
        for trajectory in self.D:
            trajectoryLs = trajectory.T
            self.allPoints += trajectoryLs
            number = len(trajectoryLs)
            self.numOfEachTra.append(number)
            self.N += number
        Rid = 1
        for indexRegion in Stop:
            stopRegion = []
            for index in indexRegion:
                stopRegion.append(self.allPoints[index])
            stopRegion_obj = Region(Rid=Rid, region=stopRegion)
            stopRegion_obj.setAttribute()
            self.stopRegionLs.append(stopRegion_obj)
            Rid += 1
            # print("Rid为",Rid)
        print("StopRegion的总数为", len(self.stopRegionLs))
        # print("stopRegionals为：", self.stopRegionLs)
        return self.stopRegionLs
