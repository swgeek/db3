#!/usr/bin/python

# checks a depot for corrupt files: i.e. checks hash of every file is same is filename
# moves files to specified dir if corrupt. Does not update database!

import os
import shutil

import DbLogger
import ShaHash
import settings

def convertToHexString(num):
    s = "%X" % num
    if len(s) < 2:
        s = "0" + s
    return s

logger = DbLogger.dbLogger()

corruptFileDir = settings.corruptFiles
sourceDepotRoot = settings.depotRoot

filecount = 0
corruptCount = 0
dircount = 0

start = 0
end = 256
#for dirname in os.listdir(sourceDepotRoot):
for i in range(start, end):
    dirname = convertToHexString(i)
    dirpath = os.path.join(sourceDepotRoot, dirname)
    if os.path.isdir(dirpath):
        logger.log("checking %d: %s" % (dircount, dirpath))

        dircount += 1
        filelist = os.listdir(dirpath)
        for filename in filelist:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                #logger.log("checking %s" % filepath)
                filecount += 1
                filehash = ShaHash.HashFile(filepath)
                filehash = filehash.upper()
                if filehash != filename:
                    logger.log("corrupt file: %s" % filepath)
                    destinationPath = os.path.join(corruptFileDir, filename)
                    logger.log("moving %s to %s" % (filepath, destinationPath))
                    shutil.move(filepath, destinationPath)
                    corruptCount += 1


logger.log("number of files: %d" % filecount)
logger.log("corrupt files: %d" % corruptCount)
