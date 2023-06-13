import math



def gaussian(x,height,center,width):
    return height*math.exp(-(x-center)*(x-center)/(2*width*width))

def mean(chunkSizes):
    total=0
    for i in range(len(chunkSizes)):
        total+=chunkSizes[i]
    return total/len(chunkSizes)


def minmaxNormalise1d(smoothed):
    curMin=float('inf')
    curMax=-float('inf')
    for data in smoothed:
        if(data<curMin):
            curMin=data
        if(data>curMax):
            curMax=data
    Range=curMax-curMin
    normalisedData=[]
    for i in range(0,len(smoothed)):
        normalisedData.append((smoothed[i]-curMin)/Range)
    return normalisedData



def gaussianSmooth(displacements,n):
    smoothed=[]
    for i in range(0,len(displacements)):
        startIdx=max(0,i-n)
        endIdx=min(len(displacements)-1,i+n)
        sumWeights = 0
        sumIndexWeight=0
        for j in range(startIdx,endIdx+1):
            indexScore=abs(j-i)/n
            indexWeight=gaussian(indexScore,1,0,1)
            sumWeights +=indexWeight*displacements[i]
            sumIndexWeight+=indexWeight
        smoothed.append(sumWeights / sumIndexWeight)
        #smoothed[i]=sumWeights/sumIndexWeight
    return smoothed
