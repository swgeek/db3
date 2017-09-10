
import os.path

import DbQueries
import DbLogger


logger = DbLogger.dbLogger()

logger.log("DIRS:")
results = DbQueries.getAllDirEntries()
dirNames = [x[1] for x in results]

for entry in sorted(dirNames):
    logger.log(entry)

logger.log("\n\nFILES: ")
results = DbQueries.getAllDirsAndFiles()
for entry in results:
    logger.log(entry)


logger.log("\n\nFILES AND LOCATIONS")
results = DbQueries.getAllFilesLocationsNamesTimestamps()
files = {}
for entry in results:
    filehash, dirpath, filename, _ = entry
    if filehash not in files:
        files[filehash] = []
    filepath = os.path.join(dirpath, filename)
    files[filehash].append(filepath)
for filehash in files:
    logger.log(filehash)
    for filepath in files[filehash]:
        logger.log("\t%s" % filepath)






