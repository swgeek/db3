# imports files into the db

import os.path
import shutil

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
            if filename.startswith("."):
                skippedFiles.append(filepath)
            else:
                fileList.append({"filename":filename, "origDirpath":dirpath})
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
        for filepath in hashesAndPaths[filehash]:
            dirpath = dirname()



    for entry in newFiles:
        filepathList = newFiles
        dirpath = entry["origDirpath"]
        if settings.startStringToRemoveFromPaths and \
                dirpath.startswith(settings.startStringToRemoveFromPaths):
            newpath = dirpath[len(settings.startStringToRemoveFromPaths):]
        else:
            newpath = dirpath
        entry["dirpath"] = newpath
        entry["dirpathHash"] = ShaHash.HashString(newpath)


def getDirsNotAlreadyInDatabase(dirhashList):
    dirsInDatabase =  DbQueries.getAllDirHashValues()
    dirsToImport = list(set(dirhashList) - set(dirsInDatabase))
    return dirsToImport


def addDirsToDatabase(dirsToImport, filesAndPaths):
    dirsToAdd = set()
    for entry in filesAndPaths:
        dirhash = entry["dirpathHash"]
        dirpath = entry["dirpath"]
        if dirhash in dirsToImport:
            dirsToAdd.add((dirhash, dirpath))

    DbQueries.addDirectories(list(dirsToAdd))


def getFilePathsNotAlreadyInDatabase(filesAndPaths):
    # convert filepaths to tuple format used by database
    pathsToImport = []
    for entry in filesAndPaths:
        dirhash = entry["dirpathHash"]
        filename = entry["filename"]
        filehash = entry["filehash"]
        pathsToImport.append((filehash, filename, dirhash))

    existingPathsInDb = DbQueries.getAllFilePaths()

    filepathsNotInDatabase = list(set(pathsToImport) - set(existingPathsInDb))

    return filepathsNotInDatabase



logger = DbLogger.dbLogger()

filelist, skippedDirs, skippedFiles = getFileList(settings.dirToImport)

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
copyFilesIntoDepot(hashesAndPaths, settings.depotRoot, logger)

DbQueries.addFiles(newFiles)

removePrefixFromDirNames(filelist)

for entry in filelist:
    print entry

# get unique dirs
# hash dirpaths
# add dirpaths to db
# add file/dirpath mappings to db
exit(1)


filesAndPathsToImport = getDirpathsAndHashes(hashesAndPaths)


dirHashes = [x["dirpathHash"] for x in filesAndPathsToImport]
newDirs = getDirsNotAlreadyInDatabase(dirHashes)
logger.log("number of dirs to import (i.e. not already in database): %d" % len(newDirs))

if newDirs:
    addDirsToDatabase(newDirs, filesAndPathsToImport)

newPaths = getFilePathsNotAlreadyInDatabase(filesAndPathsToImport)
logger.log("number of paths to import (i.e. not already in database): %d" % len(newPaths))

if newPaths:
    DbQueries.addFilepaths(newPaths)

