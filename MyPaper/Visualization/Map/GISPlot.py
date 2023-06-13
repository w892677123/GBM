# import folium
from Visualization.Colors import colorNames


class GISPlot:
    def __init__(self, rawTsLs, originPlaceLs, stopRegionLs):
        self.rawTsLs = rawTsLs
        self.stopRegionLs = stopRegionLs
        self.originPlaceLs = originPlaceLs
        self.outputPath = "Results\\Figure\\"
        self.colors = list(colorNames.keys())
        self.rawLaLong = []  # 原数据的经纬度
        self.stopRegionLaLong = []  # 结果的经纬度
        self.originPlaceLaLong = []

    def plotGIS(self, fileName):
        # 1、开始转换为带有经纬度的二维列表
        for Ts in self.rawTsLs:
            for point in Ts:
                self.rawLaLong.append([point.latitude, point.longitude])
        for stopRegion in self.stopRegionLs:
            tempLaLong = []
            stopRegionPts = stopRegion.region
            for point in stopRegionPts:
                tempLaLong.append([point.latitude, point.longitude])
            self.stopRegionLaLong.append(tempLaLong)
        # 2、画初始轨迹的地图，红色
        """# location为中心位置，zoom_start为缩放尺度, titles决定底纹样式
        # tiles = 'Stamen Terrain' (灰白)  'Stamen Toner' (黑白)
        # 街道图 http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}
        # 影像图 http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}
        # 水彩图 http://http://{s}.title.stamen.com/watercolor/{z}/{x}/{y}.jpg'
        # initiate to plotting area, tiles = 'https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'"""
        my_map = folium.Map(location=[self.rawLaLong[0][0], self.rawLaLong[0][1]],
                            zoom_start=14,
                            attr='default',
                            tiles='https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
                            )
        # 打底的红色轨迹
        folium.PolyLine(self.rawLaLong, color='red').add_to(my_map)
        # 3、画结果的轨迹地图
        # 每个簇用不同颜色
        cnt = 0
        for stopRegion in self.stopRegionLaLong:
            for pointLaLong in stopRegion:
                folium.Circle(pointLaLong
                              , radius=1.5
                              , color=self.colors[cnt % len(self.colors)]
                              , fill_color=self.colors[cnt % len(self.colors)]
                              , fillOpacity=1
                              ).add_to(my_map)
            cnt = cnt + 1
        # cnt = 0
        # for stopRegion in self.stopRegionLs:
        #     centerLocation = (stopRegion.latitude, stopRegion.longitude)  # 需要元组类型
        #     R = stopRegion.R
        #     folium.Circle(location=centerLocation
        #                   , radius=R
        #                   , color=self.colors[cnt % len(self.colors)]
        #                   , fill_color=self.colors[cnt % len(self.colors)]
        #                   , fillOpacity=1
        #                   ).add_to(my_map)
        #     cnt = cnt + 1
        my_map.save(self.outputPath + fileName + ".html")

    # 画
    def plotLabeledMap(self, fileName):
        # 1、开始转换为带有经纬度的二维列表
        # 1.1 原始轨迹 self.rawLaLong
        for Ts in self.rawTsLs:
            for point in Ts:
                self.rawLaLong.append([point.latitude, point.longitude])
        # 1.2 带标记的初始结果 self.originPlaceLaLong
        for originRegion in self.originPlaceLs:
            tempLaLong = []
            originRegionPts = originRegion.region
            for point in originRegionPts:
                tempLaLong.append([point.latitude, point.longitude])
            self.originPlaceLaLong.append(tempLaLong)
        # 1.3 聚类结果 self.stopRegionLaLong
        for stopRegion in self.stopRegionLs:
            tempLaLong = []
            stopRegionPts = stopRegion.region
            for point in stopRegionPts:
                tempLaLong.append([point.latitude, point.longitude])
            self.stopRegionLaLong.append(tempLaLong)
        # 2、画初始轨迹的地图，红色
        """# location为中心位置，zoom_start为缩放尺度, titles决定底纹样式
        # tiles = 'Stamen Terrain' (灰白)  'Stamen Toner' (黑白)
        # 街道图 http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}
        # 影像图 http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}
        # 水彩图 http://http://{s}.title.stamen.com/watercolor/{z}/{x}/{y}.jpg'
        # initiate to plotting area, tiles = 'https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'"""
        my_map = folium.Map(location=[self.rawLaLong[0][0], self.rawLaLong[0][1]],
                            zoom_start=14,
                            attr='default',
                            )
        # 2.1  # 打底的红色轨迹，散点
        # folium.PolyLine(self.rawLaLong, color='red').add_to(my_map)  # 线段图
        for pi in range(len(self.rawLaLong)):
            folium.Circle(location=(self.rawLaLong[pi][0], self.rawLaLong[pi][1])
                          , radius=0.001
                          , color='red'
                          , fill=True
                          , tooltip=str(pi)
                          ).add_to(my_map)
        # Stop打底添加其他颜色的点blue
        # for originRegion in self.stopRegionLs:
        #     for pt in originRegion.region:
        #         folium.Circle(location=(pt.latitude, pt.longitude)
        #                       , radius=0.001
        #                       , color='blue'
        #                       , fill=False
        #                       ).add_to(my_map)
        # 2.2 如果有的话, 初始簇用黑色,画圈
        # for originRegion in self.originPlaceLs:
        #     folium.Circle(location=(originRegion.centerPt.latitude, originRegion.centerPt.longitude)
        #                   , radius=originRegion.R
        #                   , color='black'
        #                   , fill=False
        #                   ).add_to(my_map)
        for originRegion in self.originPlaceLs:
            for pt in originRegion.region:
                folium.Circle(location=(pt.latitude, pt.longitude)
                              , radius=0.001
                              , color='black'
                              , fill=False
                              ).add_to(my_map)
        """folium.Circle(location=(self.originPlaceLs[3].centerPt.latitude, self.originPlaceLs[3].centerPt.longitude)
                      , radius=self.originPlaceLs[3].R
                      , color='black'
                      , fill=False
                      ).add_to(my_map)"""
        # 3、画结果的轨迹地图
        # 每个簇用不同颜色  # self.colors[cnt % len(self.colors)]
        cnt = 0
        for stopRegion in self.stopRegionLs:
            folium.Circle(location=(stopRegion.centerPt.latitude, stopRegion.centerPt.longitude)
                          , radius=stopRegion.R
                          , color='blue'
                          , fill=False
                          ).add_to(my_map)
            cnt = cnt + 1
        my_map.save(self.outputPath + fileName + ".html")

    def plotOriginMap(self, fileName):
        # 1、开始转换为带有经纬度的二维列表
        for Ts in self.rawTsLs:
            for point in Ts:
                self.rawLaLong.append([point.latitude, point.longitude])
        # 2、画初始轨迹的地图，红色
        """# location为中心位置，zoom_start为缩放尺度, titles决定底纹样式
        # tiles = 'Stamen Terrain' (灰白)  'Stamen Toner' (黑白)
        # 街道图 http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}
        # 影像图 http://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}
        # 水彩图 http://http://{s}.title.stamen.com/watercolor/{z}/{x}/{y}.jpg'
        # initiate to plotting area, tiles = 'https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'"""
        my_map = folium.Map(location=[self.rawLaLong[0][0], self.rawLaLong[0][1]],
                            zoom_start=14,
                            attr='default',
                            )
        # my_map.save(self.outputPath + "1.html")
        # 打底的红色轨迹
        # folium.PolyLine(self.rawLaLong, color='red').add_to(my_map)
        for pi in range(len(self.rawLaLong)):
            folium.Circle(location=(self.rawLaLong[pi][0], self.rawLaLong[pi][1])
                          , radius=0.001
                          , color='red'
                          , fill=True
                          , tooltip=str(pi)
                          ).add_to(my_map)
        my_map.save(self.outputPath + fileName + ".html")
