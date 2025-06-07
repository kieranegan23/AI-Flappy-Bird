import math
import random
import copy

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        #instance variables
        self.inputSize = input_size
        self.hiddenSize = hidden_size
        self.outputSize = output_size

        #create weights connecting input to hidden
        self.weightInputToHidden = []
        for _ in range(self.hiddenSize):
            hiddenWeight = []
            for _ in range(self.inputSize):
                weight = random.uniform(-1,1)
                hiddenWeight.append(weight)
            self.weightInputToHidden.append(hiddenWeight)
        
        #create a bias for hidden layer
        self.biasHidden = [random.uniform(-1, 1) for _ in range(self.hiddenSize)]

        #create weight for hidden layer
        self.weightHiddenToOutput = [random.uniform(-1, 1) for _ in range(self.hiddenSize)]

        #create bias for output
        self.biasOutput = random.uniform(-1, 1)
    
    #feedforward function  use data to determine weather to flap or not
    def feedForward(self, inputs):
        #get a list of each hidden output
        hiddenOutputs = []
        for i in range(self.hiddenSize):
            weightedSum = 0
            for weight, inputValue in zip(self.weightInputToHidden[i], inputs):
                weightedSum += weight * inputValue
            weightedSum += self.biasHidden[i]
            #use activation function
            activatedOutput = self.sigmoid(weightedSum)
            hiddenOutputs.append(activatedOutput)
        
        #add each weigthed sum together
        outputWeightedSum = 0
        for weight, hiddenOutput in zip(self.weightHiddenToOutput, hiddenOutputs):
            outputWeightedSum += weight * hiddenOutput
        outputWeightedSum += self.biasOutput 
        #use activation function
        finalOutput = self.sigmoid(outputWeightedSum) 

        return finalOutput
    
    #activation function
    def sigmoid(self, x):
        return 1 / (1 + math.exp(-x))
    
    def copy(self):
        newNN = NeuralNetwork(5,6,1)

        newNN.weightHiddenToOutput = copy.deepcopy(self.weightHiddenToOutput)
        newNN.weightInputToHidden = copy.deepcopy(self.weightInputToHidden)
        newNN.biasHidden = copy.deepcopy(self.biasHidden)
        newNN.biasOutput = copy.deepcopy(self.biasOutput)

        return newNN

    def mutate(self, mutationRate=0.1, mutationStrength=0.5):
        for i in range(len(self.weightInputToHidden)):
            for j in range(len(self.weightInputToHidden[0])):
                if random.random() < mutationRate:
                    self.weightInputToHidden[i][j] += random.uniform(-mutationStrength, mutationStrength)
    
    # Mutate weightHiddenToOutput
        for i in range(len(self.weightHiddenToOutput)):
            if random.random() < mutationRate:
                self.weightHiddenToOutput[i] += random.uniform(-mutationStrength, mutationStrength)
    
    # Mutate biasHidden
        for i in range(len(self.biasHidden)):
            if random.random() < mutationRate:
                self.biasHidden[i] += random.uniform(-mutationStrength, mutationStrength)
    
    # Mutate biasOutput
        if random.random() < mutationRate:
            self.biasOutput += random.uniform(-mutationStrength, mutationStrength)        

