from web3 import Web3
import json
import numpy as np
import binascii
import os


#
# several util functions
#


# add element by element
def addList(list1, list2):
    addedList = [sum(x) for x in zip(list1, list2)]
    return addedList

# get common elements
def getCommon(list1, list2):
    return list(set(list1).intersection(list2))

# delete list1 elements included in list2
def getDiff(list1, list2):
    return list(set(list1) - set(list2))

# delete duplicated elements
def deleteDup(mylist):
    mylist = list(dict.fromkeys(mylist))
    return mylist

def saveListAsJson(list1, filePath):
    with open(filePath, 'w') as f:
        f.write(json.dumps(list1))

def loadJsonAsList(filePath):
    jsonFile = open(filePath)
    list1 = json.load(jsonFile)
    return list1

def pickZeroElementIndex(list1):
    x = np.array(list1)
    zeroIndices = np.where(x == 0)[0]
    zeroIndices = [x for x in zeroIndices]
    zeroIndices = list(map(int, zeroIndices))
    return zeroIndices

def makeRandHexAddress():
	randHex = binascii.b2a_hex(os.urandom(20))
	return Web3.toChecksumAddress("0x" + randHex.decode('utf-8'))

def intToHexAddress(i):
    return Web3.toChecksumAddress(hex(i)[2:].zfill(40))

if __name__ == "__main__":
    list1 = [1,2,3]
    list2 = [4,5,7]
    addedList = addList(list1, list2)
    print(addedList)

    saveListAsJson(addedList, "testArray.json")

    list3 = loadJsonAsList("testArray.json")
    print(list3)

    list4 = [10,20,0,50,0,0,50,0]
    zeroIndexes = pickZeroElementIndex(list4)
    print(zeroIndexes)

    addr1 = makeRandHexAddress()
    addr2 = intToHexAddress(16**39)
    print(addr1, addr2)


    print("DONE")

