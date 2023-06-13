# !/usr/bin/env python
# -*- coding: utf-8 -*-
import jpype
import os


class HUSRM:
    def __init__(self):
        self.maximumSequenceCount = 2147483647  # JAVA中int的最大值
        self.content = ""
        self.HUSRMRes = {}
        self.stats = {}

    def run(self, minConf, minUtil, maxAntecedent, maxConsequent):
        # 1、使用jpype开启虚拟机（在开启jvm之前要加载类路径）
        curpath = os.path.abspath(".")  # 当前路径
        jarpath = os.path.join(curpath, "Jar\\Husrm.jar")
        # 获取jvm.dll的文件路径
        jvmPath = jpype.getDefaultJVMPath()
        # 开启jvm
        jpype.startJVM(jvmPath, "-ea", "-Djava.class.path=%s" % jarpath)
        # 2、加载java类（参数是java的长类名，加载什么类就调用什么类）
        HusrmClass = jpype.JClass("husrm.AlgoHUSRM")  # MainTestHUSRM_saveToFile
        # 实例化java对象
        HusrmObj = HusrmClass()
        # 3、调用java方法
        """
        定义需要的一些参数
        """
        # 读文件内容转换为content
        with open("Data\\DataBase_HUSRM.txt", "r") as fp:
            self.content = fp.read()
        # minconf = 0.70
        # minutil = 40
        # maxAntecedentSize = 4
        # maxConsequentSize = 4
        res = HusrmObj.runAlgorithm(self.content, minConf, minUtil, maxAntecedent, maxConsequent,
                                    self.maximumSequenceCount)
        stats = HusrmObj.getStats()
        """
        1、传参数传字符串,逗号分割,然后在java中处理；同时也传输入的字符串
        2、在java代码中,读取字符串保存为文件,然后在处理
        """
        # 把结果转换为dict
        resSplit = res.split("\n")
        for idx in range(len(resSplit)):
            tempRes = []
            resItem = resSplit[idx]
            ruleDict = {}
            data = resItem.split("\t")
            antecedent = list(map(str, data[0].split(",")))
            consequent = list(map(str, data[1].split(",")))
            consequent[0] = consequent[0].replace("==> ", "")
            ruleDict["support"] = float(str(data[2].split(": ")[1]))
            ruleDict["confidence"] = float(str(data[3].split(": ")[1]))
            ruleDict["utility"] = float(str(data[4].split(": ")[1]))
            tempRes.append(antecedent)
            tempRes.append(consequent)
            tempRes.append(ruleDict)
            self.HUSRMRes["rule" + str(idx + 1)] = tempRes
        statsSplit = stats.split("\n")
        self.stats["minUtility"] = float(str(statsSplit[0].split(":")[1]))
        self.stats["Sequential rules count"] = float(str(statsSplit[1].split(":")[1]))
        self.stats["Total time"] = float(str(statsSplit[2].split(":")[1]))
        self.stats["Max memory"] = float(str(statsSplit[3].split(":")[1]))
        # 4、关闭jvm
        jpype.shutdownJVM()
