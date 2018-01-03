
import os
import os.path
import shutil

import DbQueries
import DbLogger
import settings


logger = DbLogger.dbLogger()

# pretty inefficient to get every single file just to extract some
# if this ends up slow then rewrite query

results = DbQueries.getAllFilesLocationsNamesTimestamps()

filesToExtract = [x for x in results if (x[1].startswith(settings.dirToExport + "/") or x[1] == settings.dirToExport)]

filesAndNewPaths = {}
for filehash, dirpath, filename, timestamp in filesToExtract:
    #if dirpath.startswith("/"):
    #    dirpath = dirpath[1:]
    newpath = os.path.join(settings.exportDir, dirpath, filename)
    filesAndNewPaths[filehash] = (newpath, timestamp)

for filehash in filesAndNewPaths:
    sourcePath = os.path.join(settings.depotRoot, filehash[0:2], filehash)
    destinationPath, timestamp = filesAndNewPaths[filehash]

    if not os.path.isfile(sourcePath):
        logger.log("ERROR: %s does not exist" % sourcePath)
        continue # comment out or get rid of!!
        exit(1)


    if not os.path.exists(os.path.dirname(destinationPath)):
        os.makedirs(os.path.dirname(destinationPath))

    while os.path.exists(destinationPath):
        logger.log("\t%s already exists!" % destinationPath)
        basename, extension = os.path.splitext(destinationPath)
        destinationPath = basename + "_" + extension
        logger.log("\ttrying %s" % destinationPath)

    logger.log("copying %s" % destinationPath)
    shutil.copyfile(sourcePath, destinationPath)
    # set timestamp to original timestamp of file when imported
    os.utime(destinationPath,(timestamp, timestamp))