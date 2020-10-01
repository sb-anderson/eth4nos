import os
import sys
import datetime
from pathlib import Path

SYNC_START_STRING = "Block synchronisation started" # ex. INFO [09-27|12:20:31.097] Block synchronisation started
SYNC_END_STRING = "Fast Sync Finished"              # ex. INFO [09-27|12:21:30.121] Fast Sync Finished 

# syncBoundaries: 40383, 80703, 121023, 161343, 201663, 241983, 282303
EPOCH = 40320
MAX_BLOCK_NUM = 300000

LOG_PATH = "syncLogs/"
RESULT_PATH = "collectedData/"

def getSyncTimesFromFile(syncType, fileNum):

    print("\nsync type:", syncType)

    syncBoundaries = range(1, int(MAX_BLOCK_NUM/EPOCH)+1)
    syncBoundaries = [EPOCH * element for element in syncBoundaries]
    syncBoundaries = [63+element for element in syncBoundaries]
    # print("syncBoundaries:", syncBoundaries)

    for syncBoundary in syncBoundaries:
        
        # reset syncTimes
        syncTimes = list()

        # get sync times from each file
        for i in range(fileNum):

            # get file path
            filePath = LOG_PATH + syncType + "_log/" + syncType + "_" + str(syncBoundary) + "_log/" + syncType + "_" + str(syncBoundary) + "_" + str(i) + ".txt"
            # print("start analyze file ->", syncType + "_" + str(syncBoundary) + "_" + str(i) + ".txt")

            # get sync start time log
            stream = os.popen('grep ' + "\'" + SYNC_START_STRING + "\'" + " " + filePath)
            syncStartLog = stream.read()
            # print("syncStartLog:", syncStartLog)
            if syncStartLog == "":
                print("WARNING: no sync start log, this file failed fast sync ->", syncType + "_" + str(syncBoundary) + "_" + str(i) + ".txt")
                continue

            # get sync start time
            syncStartTimeString = syncStartLog[8:26]
            # print("syncStartTimeString: ", syncStartTimeString)
            syncStartTime = datetime.datetime.strptime(syncStartTimeString, "%m-%d|%H:%M:%S.%f")
            # print("syncStartTime: ", syncStartTime)

            # get sync end time log
            stream = os.popen('grep ' + "\'" + SYNC_END_STRING + "\'" + " " + filePath)
            syncEndLog = stream.read()
            # print("syncEndLog:", syncEndLog)
            if syncEndLog == "":
                print("WARNING: no sync end log, this file failed fast sync ->", syncType + "_" + str(syncBoundary) + "_" + str(i) + ".txt")
                continue

            # get sync end time
            syncEndTimeString = syncEndLog[6:24]
            # print("syncEndTimeString: ", syncEndTimeString)
            syncEndTime = datetime.datetime.strptime(syncEndTimeString, "%m-%d|%H:%M:%S.%f")
            # print("syncEndTime: ", syncEndTime)

            # calculate sync time
            elapsed = (syncEndTime - syncStartTime).total_seconds()
            # print("elapsed: ", elapsed)
            syncTimes.append(int(elapsed))

        # write sync times in a result file
        print("sync boundary:", syncBoundary, "\t-> avg time:", int(sum(syncTimes[1:])/len(syncTimes[1:])), "\t-> syncTimes:", syncTimes)
        f = open(RESULT_PATH + syncType + "/" + syncType + "_" + str(syncBoundary) + ".txt", "w+")
        for time in syncTimes:
            f.write(str(time) + "\n")
        f.close()



if __name__ == "__main__":

    syncTypes = ["eth4nos_fast", "eth4nos_compact", "geth_fast", "geth_compact"]

    for syncType in syncTypes:

        # make folders for result files
        Path(RESULT_PATH+syncType).mkdir(parents=True, exist_ok=True)

        # get sync times from log files
        getSyncTimesFromFile(syncType, 15)

    print("Done!")
