import json
import sys
def readModelParameters(filePath):
    try:
        parameters, transitionMatrix, emissionMatrix, initialProbabilityMatrix, tagMostUniqueTerms = [], [], [], [], []
        with open(filePath, 'r', encoding='utf-8', errors='ignore') as inputFile:
            parameters = json.loads(inputFile.read())
            transitionMatrix = parameters["transitionMatrix"]
            emissionMatrix = parameters["emissionMatrix"]
            initialProbabilityMatrix = parameters["initialProbabilityMatrix"]
            tagMostUniqueTerms = parameters["tagMostUniqueTerms"]

        return transitionMatrix, emissionMatrix, initialProbabilityMatrix, tagMostUniqueTerms
    except:
        print('Failure in reading model parameters from file')


def viterbiDecodingWithOpenClass(transitionMatrix, emissionMatrix, initialProbabilityMatrix, mostUniqueTermsTag, sentence):
    # Function to perform viterbi decoding with open-closed class distinction
    viterbiProb = {}
    backpointer = {}

    # Initialization Step
    for state in initialProbabilityMatrix:
        viterbiProb[state] = {0:{}}
        backpointer[state] = {}
        word = sentence.rstrip('\n').split(' ')[0]  # Take first word
        if emissionMatrix[state].get(word) == None: # If it is an unseen word which does not exist for that particular state assign only initial probability
            if state in mostUniqueTermsTag:
                viterbiProb[state][0] = initialProbabilityMatrix[state]
            else:
                viterbiProb[state][0] = 0
        else:
            viterbiProb[state][0] = initialProbabilityMatrix[state] * emissionMatrix[state][word]
        backpointer[state][0] = 0

    # Recursion Step
    wordList = sentence.rstrip('\n').split(' ')
    for idx in range(1, len(wordList)):
        for state in initialProbabilityMatrix:
            value, backPtr = 0, 0
            for sprime in initialProbabilityMatrix:
                if emissionMatrix[state].get(wordList[idx]) == None:   # For an unseen word - compute transition * viterbi
                    if state in mostUniqueTermsTag and viterbiProb[sprime][idx - 1] * transitionMatrix[sprime][state] > value:
                        value = viterbiProb[sprime][idx - 1] * transitionMatrix[sprime][state]
                        backPtr = sprime
                else: # For a seen word - compute transition * viterbi * emission    
                    if viterbiProb[sprime][idx - 1] * transitionMatrix[sprime][state] * emissionMatrix[state][wordList[idx]] > value:
                        value = viterbiProb[sprime][idx - 1] * transitionMatrix[sprime][state] * emissionMatrix[state][wordList[idx]]
                        backPtr = sprime
            viterbiProb[state][idx] = value
            backpointer[state][idx] = backPtr
    
    # Termination step
    maxPathProb, maxPathPointer = [], []
    maxVal, maxState = 0, 0
    for state in viterbiProb:
        if viterbiProb[state][len(wordList) - 1] > maxVal:
            maxVal = viterbiProb[state][len(wordList) - 1]
            maxState = state
    
    maxPathPointer.append(maxState)
    maxPathProb.append(maxVal)

    for i in range(1, len(wordList)):
        maxState = backpointer[maxState][len(wordList) - i]
        maxPathPointer.append(maxState)

    maxPathPointer.reverse()
    return maxPathPointer

def readInputFile(filepath):
    fileContent = open(filepath, 'r')
    fileContent = fileContent.readlines()
    return fileContent

def writeOutputFile(bestPath, fileContent, outputFileName):
    file = open(outputFileName, 'w')
    for idx in range(len(fileContent)):
        try:
            sentence = ''
            wordList = fileContent[idx].rstrip('\n').split(' ')
            for i in range(len(wordList) - 1):
                sentence += wordList[i] + '/' + bestPath[idx][i] + ' '
            sentence += wordList[len(wordList) - 1] + '/' + bestPath[idx][len(wordList) - 1]
            file.write(sentence +'\n')
        except:
            print(f'Error for: {fileContent[idx]}, best path: {bestPath}')
            break
    file.close()


if __name__ == "__main__":
    inputFilePath = sys.argv[1]
    fileContent = readInputFile(inputFilePath)
    bestPathPointer = []
    transitionMatrix, emissionMatrix, initialProbabilityMatrix, tagMostUniqueTerms = readModelParameters('./hmmmodel.txt')

    for sentence in fileContent:
        bestPathPointer.append(viterbiDecodingWithOpenClass(transitionMatrix, emissionMatrix, initialProbabilityMatrix, list(tagMostUniqueTerms), sentence))
    writeOutputFile(bestPathPointer, fileContent, './hmmoutput.txt')