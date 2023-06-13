# !/usr/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt


class Grubbs:
    def __init__(self):
        self.grubbsTable = [0, 0, 1.153, 1.463, 1.672, 1.822, 1.938, 2.032, 2.110, 2.176,
                            2.234, 2.285, 2.331, 2.371, 2.409, 2.443, 2.475, 2.504, 2.532, 2.557,
                            2.580, 2.603, 2.624, 2.644, 2.663, 2.681, 2.698, 2.714, 2.730, 2.745,
                            2.759, 2.773, 2.786, 2.799, 2.811, 2.823, 2.835, 2.846, 2.857, 2.866,
                            2.877, 2.887, 2.896, 2.905, 2.914, 2.923, 2.931, 2.940, 2.948, 2.956,
                            2.964, 2.971, 2.978, 2.986, 2.992, 3.000, 3.006, 3.013, 3.019, 3.025,
                            3.032, 3.037, 3.044, 3.049, 3.055, 3.061, 3.366, 3.071, 3.076, 3.082,
                            3.087, 3.092, 3.098, 3.102, 3.107, 3.111, 3.117, 3.121, 3.125, 3.130,
                            3.134, 3.139, 3.143, 3.147, 3.151, 3.155, 3.160, 3.163, 3.167, 3.171,
                            3.174, 3.179, 3.182, 3.186, 3.189, 3.193, 3.196, 3.201, 3.204, 3.207]

    def grubbs(self, outRegions, attibute):
        regions = outRegions
        while True:
            u = 0
            sigma = 0
            n = len(regions)
            if n == 0 or n > 100:
                break
            # 求均值
            for i in range(n):
                attibuteValue = eval(attibute.replace("#", "[" + str(i) + "]"))
                u = u + attibuteValue  # regions[i].startTime
            u = u / n
            # 求标准差
            for i in range(n):
                attibuteValue = eval(attibute.replace("#", "[" + str(i) + "]"))
                sigma = sigma + (attibuteValue - u) ** 2
            sigma = sqrt(sigma / n)
            x_max = eval(attibute.replace("#", "[-1]")) - u  # regions[-1].startTime - u
            x_min = eval(attibute.replace("#", "[0]")) - u  # regions[0].startTime - u
            if x_max >= x_min:
                grubbsValue = x_max / sigma
                if grubbsValue >= self.grubbsTable[n - 1]:
                    del regions[-1]
                else:
                    break
            else:
                grubbsValue = x_min / sigma
                if grubbsValue >= self.grubbsTable[n - 1]:
                    del regions[0]
                else:
                    break
        regions.sort(key=lambda region: region.Rid)
        return regions
