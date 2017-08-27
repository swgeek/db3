# imports files into the db

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
    skippedDirs = []
    for dirpath, subdirs, files in os.walk(rootDirPath):
        #make copy of subdirs before iterating as will be modifying subdirs
        subdirsCopy = subdirs[:]
        for dirname in subdirsCopy:
            if dirname.startswith("."):
                subdirpath = os.path.join(dirpath, dirname)
                skippedDirs.append(subdirpath)
                subdirs.remove(dirname)
        for filename in files:
            filepath = os.path.join(dirpath, filename)
            if filename.startswith(".") or filename.endswith(".pyc"):
                skippedFiles.append(filepath)
            else:
                timestamp = int(os.path.getmtime(filepath))
                fileList.append({"filename":filename, "origDirpath":dirpath, "timestamp":timestamp})
    return fileList, skippedDirs, skippedFiles


def hashFiles(filelist):
    for fileinfo in filelist:
        filepath = os.path.join(fileinfo["origDirpath"], fileinfo["filename"])
        filehash = ShaHash.HashFile(filepath)
        filehash = filehash.upper()
        fileinfo["filehash"] = filehash


def getFilesNotAlreadyInDatabase(filehashSet):
    filesInDatabase =  DbQueries.getAllFilehashValues()
    # only want to copy files not in database
    filesNotInDatabase = list(set(filehashSet) - set(filesInDatabase))
    return filesNotInDatabase


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


parser = argparse.ArgumentParser()
parser.add_argument("dirToImport", nargs=1, help="directory to import")
parser.add_argument("-n", action="store_true", help="don't actually import. This is just to check what files would be imported")
args = parser.parse_args()

dontImport = args.n
dirToImport = args.dirToImport[0]

logger = DbLogger.dbLogger()

logger.log("don't import flag: %r" % dontImport)
logger.log("directory to import: %s" % dirToImport)

filelist, skippedDirs, skippedFiles = getFileList(dirToImport)

for dirpath in skippedDirs:
    logger.log("skipping dir %s" % dirpath)
logger.log("\n")

for filepath in skippedFiles:
    logger.log("skipping file %s" % filepath)
logger.log("\n")

hashFiles(filelist)

filehashSet = set([x["filehash"] for x in filelist])
newFiles = getFilesNotAlreadyInDatabase(filehashSet)
logger.log("number of unique files: %d" % len(filehashSet))
logger.log("number of unique files to copy (i.e. not already in depot): %d" % len(newFiles))

hashesAndPaths = getFilePathsForFilehash(newFiles, filelist)

# TODO: also print out filepaths for this flag, but don't add them of course
if dontImport:
    allpaths = hashesAndPaths.values()
    allpaths.sort()
    for filepath in allpaths:
        logger.log("would import: %r" % filepath)
    exit(1)

copyFilesIntoDepot(hashesAndPaths, settings.depotRoot, logger)
DbQueries.addFiles(newFiles)

removePrefixFromDirNames(filelist)
uniqueDirs = getUniqueDirectories(filelist)
hashToDirpathMapping = hashDirpaths(uniqueDirs)
newDirs = getDirsNotAlreadyInDatabase(hashToDirpathMapping.keys())

logger.log("number of dirs to import (i.e. not already in database): %d" % len(newDirs))

addDirsToDatabase(newDirs, hashToDirpathMapping)

addDirpathHashToEntries(filelist, hashToDirpathMapping)

newPaths = getFilePathsNotAlreadyInDatabase(filelist)

if newPaths:
    logger.log("number of paths to import (i.e. not already in database): %d" % len(newPaths))
    addFilepathsToDatabase(newPaths, filelist)
