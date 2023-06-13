# !/usr/bin/env python
# -*- coding: utf-8 -*-


# import jpype
# import os
#
# # 1、使用jpype开启虚拟机（在开启jvm之前要加载类路径）
# curpath = os.path.abspath(".")  # 当前路径
# # curpath = "D:\ProgramCodes\Python\PyCharm\MyPaper"
# jarpath = os.path.join(curpath, "Husrm.jar")
# # jarpath,将a和b拼成路径jarpath\Myproject.jar
# # 获取jvm.dll的文件路径
# jvmPath = jpype.getDefaultJVMPath()
# # 开启jvm
# jpype.startJVM(jvmPath, "-ea", "-Djava.class.path=%s" % jarpath)
# # 2、加载java类（参数是java的长类名，加载什么类就调用什么类）
# HusrmClass = jpype.JClass("husrm.AlgoHUSRM")  # MainTestHUSRM_saveToFile
# # 实例化java对象
# HusrmObj = HusrmClass()
# # 3、调用java方法
# """
# 定义需要的一些参数
# """
# # 读文件内容转换为content
# with open("DataBase_HUSRM.txt", "r") as fp:
#     content = fp.read()
# minconf = 0.70
# minutil = 40
# maxAntecedentSize = 4
# maxConsequentSize = 4
# maximumSequenceCount = 2147483647  # JAVA中int的最大值
# res = HusrmObj.runAlgorithm(content, minconf, minutil, maxAntecedentSize, maxConsequentSize,
#                             maximumSequenceCount)
# stats = HusrmObj.getStats()
# print(res)
# print(stats)
#
# """
# 1、传参数传字符串,逗号分割,然后在java中处理；同时也传输入的字符串
# 2、在java代码中,读取字符串保存为文件,然后在处理
# """
# # 4、关闭jvm
# jpype.shutdownJVM()


from Core.HUSRM import HUSRM

HUSRM_obj = HUSRM()
HUSRM_obj.run(0.7, 40, 4, 4)
print(HUSRM_obj.HUSRMRes)
