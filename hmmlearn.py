import sys
from copy import deepcopy
import json
from collections import Counter

def countTagOccurrences(file):
    # Count number of times a tag occurs in the corpus
    tagOccurences = {}
    for sentence in file:
        for word in sentence.rstrip('\n').split(' '):
            try:
                wordSplit = word.split('/')
                tag = wordSplit[-1]
                tagOccurences[tag] = tagOccurences.get(tag, 0) + 1
            except:
                print('Failed for \n\n\n=============\n\n')
                print(f'Sentence {sentence}\nWord {word}\nTag {tag}\n==================')
    return tagOccurences

def countTagFollowOccurences(file):
    # Counting the number of times a tag follows another tag i.e Si-1 -> Si
    tagFollowOccurences = {}
    allTags = []
    for sentence in file:
        allTagsInSentence = []
        for word in sentence.rstrip('\n').split(' '):
            try:
                tag = word.split('/')[-1]
                allTags.append(tag)
                allTagsInSentence.append(tag)
            except:
                print('Failed for \n\n\n=============\n\n')
                print(f'Sentence {sentence}\nWord {word}\nTag {tag}\n==================')
        for idx in range(0, len(allTagsInSentence) - 1):
            if tagFollowOccurences.get(allTagsInSentence[idx]) == None: # Here we check if the i-1 tag exists in the dictionary. If it doesn't - we create its associated dictionary
                tagFollowOccurences[allTagsInSentence[idx]] = {}
            if idx + 1 < len(allTagsInSentence):
                tagFollowOccurences[allTagsInSentence[idx]][allTagsInSentence[idx+1]] = tagFollowOccurences[allTagsInSentence[idx]].get(allTagsInSentence[idx+1], 0) + 1

    allTags = list(set(allTags))
    for i in allTags:
        for j in tagFollowOccurences:
            if tagFollowOccurences[j].get(i) == None:
                tagFollowOccurences[j][i] = 0

    return tagFollowOccurences

def createWordTagOccurrences(file):
    # Format for counting the number of times a tag is associated with a word
    # {Tag1: {Word1: count1, word2:count2, .....}, Tag2: {Word1: count1, word2:count2, .....}, ....}
    wordTagOccurrences = {}
    setUniqueWords = []

    for sentence in file:
        for word in sentence.rstrip('\n').split(' '):
            try:
                splitWords = word.split('/')
                word = splitWords[0]
                setUniqueWords.append(word)
                tag = splitWords[-1]
                if wordTagOccurrences.get(tag) == None:
                    wordTagOccurrences[tag] = {}
                wordTagOccurrences[tag][word] = wordTagOccurrences[tag].get(word, 0) + 1
            except:
                print('Failed for \n\n\n=============\n\n')
                print(f'Sentence {sentence}\nWord {word}\nTag {tag}\n==================')

    setUniqueWords = list(set(setUniqueWords))
    for i in setUniqueWords:
        for j in wordTagOccurrences:
            if wordTagOccurrences[j].get(i) == None:
                wordTagOccurrences[j][i] = 0
    return wordTagOccurrences

def createTransitionProbMatrix(tagOccurences, tagFollowOccurences):
    # Creating the transition probability matrix by utilizing the outputs of countTagOccurrences() and countTagFollowOccurences()
    transitionProbability = deepcopy(tagFollowOccurences)
    for i in transitionProbability:
        for j in transitionProbability[i]:
            transitionProbability[i][j] = (tagFollowOccurences[i][j] + 1)/ (tagOccurences[i] + len(tagOccurences))  # Performing smoothing
    
    for i in tagOccurences:
        if transitionProbability.get(i) == None:
            transitionProbability[i] = deepcopy(tagOccurences)
            for key in transitionProbability[i]:
                transitionProbability[i][key] = 1 / (tagOccurences[i] + len(tagOccurences))
 
    return transitionProbability
    

def createEmissionProbMatrix(tagOccurences, wordTagOccurrences):
    # Creating the emission probability matrix by utilizing the outputs of countTagOccurrences() and createWordTagOccurrences()
    emissionProbability = deepcopy(wordTagOccurrences)
    for i in emissionProbability:
        for j in emissionProbability[i]:
            emissionProbability[i][j] = (wordTagOccurrences[i][j]) / (tagOccurences[i])
    return emissionProbability


def createInitialProbabilityMatrix(file, initialProbabilityMatrix, uniqueTagsLength):
    # Creating the initial probability matrix by counting the number of times a sentence starts with a particular tag / total number of sentences
    tagList = []
    numberOfSentences = 0
    for sentence in file:
        word = sentence.rstrip('\n').split(' ')[0]
        try:
            splitWords = word.split('/')
            tag = splitWords[-1]
            tagList.append(tag)
            numberOfSentences += 1
        except:
            print('Failed for \n\n\n=============\n\n')
            print(f'Sentence {sentence}\nWord {word}\nTag {tag}\n==================')
    tagCounter = Counter(tagList)

    for i in tagCounter:
        tagCounter[i] = (tagCounter[i] + 1) / (numberOfSentences + uniqueTagsLength)
    for i in initialProbabilityMatrix:
        initialProbabilityMatrix[i] = tagCounter[i] if tagCounter.get(i) != None else (1 / (numberOfSentences + uniqueTagsLength))

    return initialProbabilityMatrix

def tagMostUniqueTerms(file):
    # Identifying the top 5 tags with the most unique words associated with it
    # Done for open-closed class distinction   
    tagMostUniqueTerms = {}
    for sentence in file:
        for word in sentence.rstrip('\n').split(' '):
            try:
                wordSplit = word.split('/')
                tag = wordSplit[-1]
                if tagMostUniqueTerms.get(tag) == None:
                    tagMostUniqueTerms[tag] = []
                tagMostUniqueTerms[tag].append(wordSplit[0])
            except:
                print('Failed for \n\n\n=============\n\n')
                print(f'Sentence {sentence}\nWord {word}\nTag {tag}\n==================')
    
    for tag in tagMostUniqueTerms:
        tagMostUniqueTerms[tag] = len(set(tagMostUniqueTerms[tag]))
    tagMostUniqueTerms = sorted(list(tagMostUniqueTerms.items()), key=lambda x:x[1], reverse=True)
    tagMostUniqueTerms = dict(tagMostUniqueTerms[:5])

    return tagMostUniqueTerms



def readInputFile(filepath):
    fileContent = open(filepath, 'r')
    fileContent = fileContent.readlines()
    return fileContent

def writeParameters(filePath, weightDictionary):
    with open(filePath, 'w', encoding='utf-8') as outputFile:
        json.dump(weightDictionary, outputFile, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    inputFilePath = sys.argv[1]
    fileContent = readInputFile(inputFilePath)
    tagOccurences = countTagOccurrences(fileContent)

    tagMostUniqueTerms = tagMostUniqueTerms(fileContent)

    tagFollowOccurences = countTagFollowOccurences(fileContent)
    transitionMatrix = createTransitionProbMatrix(tagOccurences, tagFollowOccurences)
    
    wordTagOccurrences = createWordTagOccurrences(fileContent)
    emissionMatrix = createEmissionProbMatrix(tagOccurences, wordTagOccurrences)
    
    initialProbabilityMatrix = deepcopy(tagOccurences)
    initialProbabilityMatrix = createInitialProbabilityMatrix(fileContent, initialProbabilityMatrix, len(tagOccurences))

    weightDictionary = {"transitionMatrix": transitionMatrix, "emissionMatrix": emissionMatrix, "initialProbabilityMatrix": initialProbabilityMatrix, "tagMostUniqueTerms": tagMostUniqueTerms}
    writeParameters('./hmmmodel.txt', weightDictionary)