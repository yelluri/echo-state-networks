#Run this script to run the experiment
#Steps to follow are:
# 1. Preprocessing of data
# 2. Give the data to the reservoir
# 3. Plot the performance (such as error rate/accuracy)

from reservoir import ClassicESN as ESN
from plotting import OutputPlot as outputPlot
import numpy as np
import os
from datetime import datetime
from sklearn import preprocessing as pp
from reservoir import Utility as util
from performance import RootMeanSquareError as rmse

# Read data from the file
data = np.loadtxt('MackeyGlass_t17.txt')

# Normalize the raw data
minMax = pp.MinMaxScaler((-1,1))
data = minMax.fit_transform(data)

#Get only 4000 points
data = data[:4000].reshape((4000, 1))

# Number of points - 4000
trainingData, validationData = util.splitData2(data, 0.5)
nTesting = validationData.shape[0]
validationData = validationData.reshape((nTesting, 1))

# Form feature vectors
inputTrainingData, outputTrainingData = util.formFeatureVectors(trainingData)

# Tune the network
size = 256
initialTransient = 50

res = ESN.Reservoir(size=size,
                               inputData=inputTrainingData,
                               outputData=outputTrainingData,
                               spectralRadius=0.8212078,
                               inputScaling=0.28820175,
                               reservoirScaling=0.23426303,
                               leakingRate=0.28772191,
                               initialTransient=initialTransient)
res.trainReservoir()


#Warm up
predictedTrainingOutputData = res.predict(inputTrainingData)


#Predict future values
predictedTestOutputData = util.predictFuture(res, trainingData[-1], nTesting)

#Calculate the error
errorFunction = rmse.RootMeanSquareError()
error = errorFunction.compute(validationData, predictedTestOutputData)
print("Regression error:"+str(error))


#Plotting of the prediction output and error
outputFolderName = "Outputs/Outputs" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
os.mkdir(outputFolderName)
outplot = outputPlot.OutputPlot(outputFolderName + "/Prediction.html", "Mackey-Glass Time Series", "Prediction of future values", "Time", "Output")
outplot.setXSeries(np.arange(1, nTesting + 1))
outplot.setYSeries('Actual Output', minMax.inverse_transform(validationData[:nTesting, 0]))
outplot.setYSeries('Predicted Output', minMax.inverse_transform(predictedTestOutputData[:nTesting, 0]))
outplot.createOutput()
print("Done!")