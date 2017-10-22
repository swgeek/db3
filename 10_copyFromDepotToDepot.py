#!/usr/bin/python

# copy all files from one depot into another that do not exist in that depot
import os
import shutil

import DbLogger


def CopyFileIntoDepotIfDoesNotExist(depotRootPath, sourceFilePath, filehash, logger):
        subdir = filehash[0:2]
        destinationDirPath = os.path.join(depotRootPath, subdir)
        destinationFilePath = os.path.join(depotRootPath, subdir, filehash)

        if not os.path.isdir(destinationDirPath):
            os.mkdir(destinationDirPath)

        if os.path.isfile(destinationFilePath):
            #logger.log( "%s already exists" % destinationFilePath )
            pass
        else:
            logger.log("copying %s to %s" % (sourceFilePath, destinationFilePath))
            #shutil.copyfile(sourceFilePath, destinationFilePath)
            #shutil.movefile(sourceFilePath, destinationFilePath)
            shutil.copyfile(sourceFilePath, destinationFilePath)


def convertToHexString(num):
    s = "%X" % num
    if len(s) < 2:
        s = "0" + s
    return s


logger = DbLogger.dbLogger()

sourceDepotRoot = "/Volumes/m2/depot"
destDepotRoot = "/Volumes/db/depot"


# skip non directories
start = 0
end = 256

dircount = 0
for i in range(start, end):
    subdir = convertToHexString(i)
    subdirpath = os.path.join(sourceDepotRoot, subdir)
    if not os.path.isdir(subdirpath):
        logger.log("%s does not exist in source, skipping" % subdirpath)
        continue

    logger.log("source directory %s" % subdirpath)

    destdirpath = os.path.join(destDepotRoot, subdir)
    if not os.path.isdir(destdirpath):
        logger.log("%s does not exist in dest, making dir" % destdirpath)
        os.mkdir(destdirpath)

    logger.log("dest directory %s" % destdirpath)

    filelist = os.listdir(subdirpath)

    for filename in filelist:
            #logger.log("\tchecking %s" % filename)
            # TODO: check if filehash and not random file
            filepath = os.path.join(subdirpath, filename)
            destpath = os.path.join(destdirpath, filename)
            CopyFileIntoDepotIfDoesNotExist(destDepotRoot, filepath, filename, logger)


