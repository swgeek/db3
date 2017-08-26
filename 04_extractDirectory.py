
import os.path
import shutil

import DbQueries
import DbLogger
import settings


logger = DbLogger.dbLogger()

# pretty inefficient to get every single file just to extract some
# if this ends up slow then rewrite query

results = DbQueries.getAllFilesLocationsNames()
filesToExtract = [x for x in results if x[1].startswith(settings.dirToExport)]

filesAndNewPaths = {}
for filehash, dirpath, filename in filesToExtract:
    newpath = os.path.join(settings.exportDir, dirpath, filename)
    filesAndNewPaths[filehash] = newpath

for filehash in filesAndNewPaths:
    sourcePath = os.path.join(settings.depotRoot, filehash[0:2], filehash)
    destinationPath = filesAndNewPaths[filehash]

    if not os.path.isfile(sourcePath):
        logger.log("ERROR: %s does not exist" % sourcePath)
        exit(1)

    if not os.path.exists(os.path.dirname(destinationPath)):
        os.makedirs(os.path.dirname(destinationPath))

    logger.log("copying %s" % destinationPath)
    shutil.copyfile(sourcePath, destinationPath)

