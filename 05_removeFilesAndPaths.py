# for any file in given subdir, if that file exists in the db all traces are removed

import os.path
import shutil
import time
import argparse

import DbLogger
import ShaHash
import settings
import DbQueries


# simple filter, remove files and dirs starting with "."
# if get more complicated, pass in filters as parameters and use regex
def getFileList(rootDirPath):
    fileList = []
    skippedFiles = []
    for dirpath, subdirs, files in os.walk(rootDirPath):
        for filename in files:
            filepath = os.path.join(dirpath, filename)
            if filename.startswith("."):
                skippedFiles.append(filepath)
            else:
                timestamp = int(os.path.getmtime(filepath))
                fileList.append({"filename":filename, "origDirpath":dirpath, "timestamp":timestamp})
    return fileList, skippedFiles


def hashFiles(filelist):
    for fileinfo in filelist:
        filepath = os.path.join(fileinfo["origDirpath"], fileinfo["filename"])
        filehash = ShaHash.HashFile(filepath)
        filehash = filehash.upper()
        fileinfo["filehash"] = filehash


def getMatchedFilesInDatabase(filehashSet):
    filesInDatabase =  DbQueries.getAllFilehashValues()
    # there has to be a built in command for this, find it
    matchedFiles = [x for x in filehashSet if x in filesInDatabase]
    return matchedFiles


def getAllFilepathsFromDatabase():
    # UGH, horrible way to do this. Find the correct query
    allFiles = DbQueries.getAllFilePaths()
    hashesAndPaths = {}
    for entry in allFiles:
        filehash, filename, dirPathHash = entry
        if filehash not in hashesAndPaths:
            hashesAndPaths[filehash] = []
        hashesAndPaths[filehash].append((dirPathHash, filename))
    return hashesAndPaths


def getAllDirpathsFromDatabase():
    allDirEntries = DbQueries.getAllDirEntries()
    hashesAndDirpaths = {}
    for entry in allDirEntries:
        dirhash, dirpath = entry
        hashesAndDirpaths[dirhash] = dirpath
    return hashesAndDirpaths


def getFilePathsForFilehash(newFiles, filelist):
    filehashFilePathMapping = {}
    for entry in filelist:
        filehash = entry["filehash"]
        if (filehash in newFiles) and (filehash not in filehashFilePathMapping):
            filehashFilePathMapping[filehash] = os.path.join(entry["origDirpath"], entry["filename"])
    return filehashFilePathMapping


def copyFilesIntoDepot(hashesAndPaths, depotRootPath, logger):
    for filehash in hashesAndPaths:
        sourceFilePath = hashesAndPaths[filehash]
        depotSubdir =  filehash[0:2]
        destinationDirPath = os.path.join(depotRootPath, depotSubdir)
        destinationFilePath = os.path.join(depotRootPath, depotSubdir, filehash)

        if not os.path.isdir(destinationDirPath):
            os.mkdir(destinationDirPath)

        # always copy, even if file exists.
        # If copy interrupted file may be corrupt, but a reimport will fix
        logger.log("copying %s to %s" % (sourceFilePath, destinationFilePath))
        shutil.copyfile(sourceFilePath, destinationFilePath)



def deleteFileFromDepot(filehash, depotRootPath, logger):
    depotSubdir =  filehash[0:2]
    filepath = os.path.join(depotRootPath, depotSubdir, filehash)
    if os.path.isfile(filepath):
        logger.log("\tdeleting file %s" % filepath)
        os.remove(filepath)
    else:
        logger.log("\tcould not delete file %s - no such file" % filepath)


def removePrefixFromDirNames(filelist):
    for entry in filelist:

        origDirpath = entry["origDirpath"]
        newpath = origDirpath
        if settings.startStringToRemoveFromPaths and \
                origDirpath.startswith(settings.startStringToRemoveFromPaths):
            newpath = origDirpath[len(settings.startStringToRemoveFromPaths):]
        entry["dirpath"] = newpath


def getUniqueDirectories(filelist):
    allDirs = set()
    for entry in filelist:
        allDirs.add(entry["dirpath"])
    return allDirs


def hashDirpaths(dirpathsToHash):
    hashToPathMapping = {}
    for dirpath in dirpathsToHash:
        dirpathHash = ShaHash.HashString(dirpath)
        hashToPathMapping[dirpathHash] = dirpath
    return hashToPathMapping


def getDirsNotAlreadyInDatabase(dirhashList):
    dirsInDatabase =  DbQueries.getAllDirHashValues()
    dirsToImport = list(set(dirhashList) - set(dirsInDatabase))
    return dirsToImport


def addDirsToDatabase(dirHashes, dirhashToPathMapping):
    dirsToAdd = []
    for dirhash in dirHashes:
        dirpath = dirhashToPathMapping[dirhash]
        dirsToAdd.append((dirhash, dirpath))
    DbQueries.addDirectories(list(dirsToAdd))


def addDirpathHashToEntries(filelist, dirhashToPathMapping):
    # need pathToHash mapping
    pathToHashMapping = {v:k for k,v in dirhashToPathMapping.iteritems()}
    for entry in filelist:
        entry["dirpathHash"] = pathToHashMapping[entry["dirpath"]]


def getFilePathsNotAlreadyInDatabase(filelist):
    # convert filepaths to tuple format used by database
    pathsToImport = []
    for entry in filelist:
        dirhash = entry["dirpathHash"]
        filename = entry["filename"]
        filehash = entry["filehash"]
        pathsToImport.append((filehash, filename, dirhash))
    existingPathsInDb = DbQueries.getAllFilePaths()
    filepathsNotInDatabase = list(set(pathsToImport) - set(existingPathsInDb))
    return filepathsNotInDatabase


def addFilepathsToDatabase(filepaths, filelist):
    valuesToAdd = []
    for entry in filelist:
        dirhash = entry["dirpathHash"]
        filename = entry["filename"]
        filehash = entry["filehash"]
        timestamp = entry["timestamp"]
        if (filehash, filename, dirhash) in filepaths:
            valuesToAdd.append((filehash, filename, dirhash, timestamp))
    DbQueries.addFilepaths(valuesToAdd)


def removePath(filehash, dirhash, filename):
    DbQueries.deleteFilepath(filehash, filename, dirhash)

parser = argparse.ArgumentParser()
parser.add_argument("dirToCheck", nargs=1, help="directory to check")
parser.add_argument("-n", action="store_true", help="don't actually remove locations. This is just to check what locations would be removed")
args = parser.parse_args()

dontDelete = args.n
sourceDir = args.dirToCheck[0]

logger = DbLogger.dbLogger()

logger.log("list only/don't remove flag: %r" % dontDelete)
logger.log("directory to check: %s" % sourceDir)

filelist, skippedFiles = getFileList(sourceDir)

for filepath in skippedFiles:
    logger.log("skipping file %s" % filepath)
logger.log("\n")

hashFiles(filelist)

filehashSet = set([x["filehash"] for x in filelist])

matchedFilesInDatabase = getMatchedFilesInDatabase(filehashSet)

logger.log("number of unique files: %d" % len(filehashSet))
logger.log("number of unique files found in database: %d" % len(matchedFilesInDatabase))

hashesAndPaths = getAllFilepathsFromDatabase()

dirhashsAndDirpaths = getAllDirpathsFromDatabase()

for filehash in matchedFilesInDatabase:
    logger.log(filehash)
    pathlist = hashesAndPaths.get(filehash)
    if not pathlist:
        logger.log("\tno path entries found")
    else:
        for dirhash, filename in pathlist:
            dirpath = dirhashsAndDirpaths[dirhash]
            if dontDelete:
                logger.log( "\t%s, %s" % (dirpath, filename))
            else:
                logger.log("\t%s, %s, %s" % (dirhash, dirpath, filename))
                removePath(filehash, dirhash, filename)

    logger.log("\tremoving file from files table")
    DbQueries.deleteFilehash(filehash)
    logger.log("\tremoving file from depot")
    deleteFileFromDepot(filehash, settings.depotRoot, logger)

