#!/usr/bin/python

# TODO: merge this with 05_removeFilesAndPaths.py

# TODO: not very efficient, use sql query to get empty dirs instead
import os.path

import DbQueries
import DbLogger


logger = DbLogger.dbLogger()

# get directories
results = DbQueries.getAllDirEntries()

dirhashToDirpathMapping = {}
for entry in results:
    dirhashToDirpathMapping[entry[0]] = entry[1]

nonEmptyDirs = set()
# get files and corresponding directories
results = DbQueries.getAllFilePaths()
for filehash, filename, dirpathHash in results:
    nonEmptyDirs.add(dirpathHash)

emptyDirs = set(dirhashToDirpathMapping.keys()) - nonEmptyDirs

logger.log("removing empty dirs:")
for dirpathHash in emptyDirs:
    logger.log("\tremoving %s" % dirhashToDirpathMapping[dirpathHash])
    DbQueries.removeDirectory(dirpathHash)
# TODO: create a -n flag
# TODO: remove directory from db




