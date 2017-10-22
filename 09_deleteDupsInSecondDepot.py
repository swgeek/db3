#!/usr/bin/python

# delete files in second depot that already exist in first depot

import os
import shutil

import DbLogger

def convertToHexString(num):
    s = "%X" % num
    if len(s) < 2:
        s = "0" + s
    return s

logger = DbLogger.dbLogger()

mainDepotRoot = "/Volumes/db/depot"
secondDepotRoot = "/Volumes/db/depot4"

deleteCount = 0
keepCount = 0

start = 0
end = 256

for i in range(start, end):
    dirname = convertToHexString(i)
    dirpath = os.path.join(mainDepotRoot, dirname)
    dirpath2 = os.path.join(secondDepotRoot, dirname)
    if os.path.isdir(dirpath):
        logger.log("checking %s" % dirpath2)

        filelist1 = set(os.listdir(dirpath))
        filelist2 = set(os.listdir(dirpath2))

        for filename in filelist2:
            # TODO: set intersection!! better than this...

            if filename in filelist1:
                # delete file
                filepath = os.path.join(dirpath2, filename)
                os.remove(filepath)
                deleteCount += 1
            else:
                keepCount += 1

logger.log("deleted %d duplicate files" % deleteCount)
logger.log("kept %d new files" % keepCount)

