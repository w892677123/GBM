import math

class VariateKMeans:
    def __init__(self,stopProbabilities):
        #self.total=[]
        #self.mean=[]
        #self.values=[]
        self.Clusters=[[],[]]
        self.stopPrs=stopProbabilities


    #def update(self):
        #for cluster in self.Clusters:
            #for i in range(0,len(cluster)):
                #total[i]
        #self.mean=self.total/len(cluster)

    def reassign(self,clusterIdx):
        movedValue =0
        clusterToReassign = self.Clusters[clusterIdx]
        #c1Iter=iter(clusterToReassign)
        index_x=0
        for x in clusterToReassign:
        #for flag in clusterToReassign:#c1Iter:
            index_x+=1
            value=x
            mean=0
            for i in clusterToReassign:
                mean+=i
            mean =mean/len(clusterToReassign)
            bestDist=abs(mean-value)
            betterCluster = []
            for i in range(0,len(self.Clusters)):##看看mean对不对
                if(i==clusterIdx):
                    continue
                otherCluster=self.Clusters[i]
                mean2=0
                for tmp in otherCluster:
                    mean2 += tmp
                mean2 = mean2 / len(otherCluster)
                distToOtherCluster = abs(mean2 - value)
                if(distToOtherCluster<bestDist):
                    bestDist = distToOtherCluster
                    betterCluster = otherCluster
            if(betterCluster!=[]):
                del clusterToReassign[index_x-1]#(flag)
                #c1Iter.remove()###
                #clusterToReassign.total -= value###
                betterCluster.append(value)
                movedValue=1
        return movedValue


    def run(self,k):

       # POSMIT_obj = POSMIT(trajectoryLs)
        splitSize = (len(self.stopPrs)-1) /k  ##在UnivariateMeans里是22行 2代表k
        for i in range(1, len(self.stopPrs)):
            clusterIdx = int(math.ceil(i / splitSize)) - 1
            self.Clusters[clusterIdx].append(self.stopPrs[i])##clusters的update我暂时还没实现，需要吗？？？

        #print("Cluster1",self.Clusters[0])
        #print("Cluster2", self.Clusters[1])
        ###self.update()###
        keepClustering=1
        while(keepClustering):
            reassignedValue = 0
            for i in range(0,k):
                if(self.reassign(i)):
                    reassignedValue = 1
            #if(reassignedValue):
                ###self.update()

            keepClustering=reassignedValue
        return self.Clusters