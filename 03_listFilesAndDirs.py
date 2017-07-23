
import os.path

import DbQueries
import DbLogger


logger = DbLogger.dbLogger()

logger.log("DIRS:")
results = DbQueries.getAllDirEntries()
for entry in results:
    logger.log(entry[1])


logger.log("\n\nFILES: ")
results = DbQueries.getAllDirsAndFiles()
for entry in results:
    logger.log(entry)


logger.log("\n\nFILES AND LOCATIONS")
results = DbQueries.getAllFilesLocationsNames()
files = {}
for entry in results:
    filehash, dirpath, filename = entry
    if filehash not in files:
        files[filehash] = []
    filepath = os.path.join(dirpath, filename)
    files[filehash].append(filepath)
for filehash in files:
    logger.log(filehash)
    for filepath in files[filehash]:
        logger.log("\t%s" % filepath)






