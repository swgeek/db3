# imports files into the db

import os.path
import shutil

import DbLogger
import ShaHash
import settings
import DbQueries


def hashAllFilesInDir(rootDirPath):
    allFilesInDir = []
    for dirpath, subdirList, subdirFiles in os.walk(rootDirPath):
        for filename in subdirFiles:
            filepath = os.path.join(dirpath, filename)
            filehash = ShaHash.HashFile(filepath)
            filehash = filehash.upper()
            fileinfo = {"filehash":filehash, "origDirpath":dirpath, "filename":filename}
            allFilesInDir.append(fileinfo)
    return allFilesInDir


# removes files that we don't want to import, e.g. the annoying cookies MacOs leaves.
def filterFiles(allFiles):
    keep = []
    skip = []
    for entry in allFiles:
        filename = entry["filename"]
        if filename.startswith("."):
            skip.append(entry)
        else:
            keep.append(entry)
    return keep, skip


def getFilesNotAlreadyInDatabase(filehashlist):
    filesInDatabase =  DbQueries.getAllFilehashValues()
    # only want to copy files not in database
    filesNotInDatabase = list(set(filehashlist) - set(filesInDatabase))
    return filesNotInDatabase


def getFirstFilePathsForFiles(filesToFind, filesAndPaths):
    filesToFindSet = set(filesToFind)
    firstFilePaths = {}
    for entry in filesAndPaths:
        filehash = entry["filehash"]
        if filehash in firstFilePaths:
            continue # already have this file
        if filehash not in filesToFindSet:
            continue  # not interested in this file
        filepath = os.path.join(entry["dirpath"], entry["filename"])
        firstFilePaths[filehash] = filepath
    return firstFilePaths


def copyFilesIntoDepot(filepaths, depotRootPath, logger):
    for filehash in filepaths:
        sourceFilePath = filepaths[filehash]
        depotSubdir =  filehash[0:2]
        destinationDirPath = os.path.join(depotRootPath, depotSubdir)
        destinationFilePath = os.path.join(depotRootPath, depotSubdir, filehash)

        if not os.path.isdir(destinationDirPath):
            os.mkdir(destinationDirPath)

        # always copy, even if file exists.
        # If copy interrupted file may be corrupt, but a reimport will fix
        logger.log("copying %s to %s" % (sourceFilePath, destinationFilePath))
        shutil.copyfile(sourceFilePath, destinationFilePath)


def getRelativePathsAndHashes(filesAndPaths):
    for entry in filesAndPaths:
        dirpath = entry["origDirpath"]
        if not settings.baseDirToRemoveFromPaths:
            newpath = dirpath
        else:
            newpath = os.path.relpath(dirpath, settings.baseDirToRemoveFromPaths)
        entry["dirpath"] = newpath
        entry["dirpathHash"] = ShaHash.HashString(newpath)


def getDirsNotAlreadyInDatabase(dirhashList):
    dirsInDatabase =  DbQueries.getAllDirHashValues()
    dirsToImport = list(set(dirhashList) - set(dirsInDatabase))
    return dirsToImport


def addDirsToDatabase(dirsToImport, filesAndPaths):
    dirsToAdd = set()
    dirsToImportSet = set(dirsToImport)
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

allFilesAndPaths = hashAllFilesInDir(settings.dirToImport)
logger.log("total number filepaths: %d" % len(allFilesAndPaths))

filesAndPathsToImport, filesToSkip = filterFiles(allFilesAndPaths)
logger.log("number of filepaths after filtering: %d" % len(filesAndPathsToImport))

logger.log("Skipping files: ")
for entry in filesToSkip:
    logger.log("\t%r" % entry)

filehashlist = [x["filehash"] for x in allFilesAndPaths]
newFiles = getFilesNotAlreadyInDatabase(filehashlist)
logger.log("number of unique files: %d" % len(set(filehashlist)))
logger.log("number of unique files to copy (i.e. not already in depot): %d" % len(newFiles))

newFilePaths = getFirstFilePathsForFiles(newFiles, filesAndPathsToImport)

copyFilesIntoDepot(newFilePaths, settings.depotRoot, logger)
DbQueries.addFiles(newFiles)

getRelativePathsAndHashes(filesAndPathsToImport)

dirHashes = [x["dirpathHash"] for x in filesAndPathsToImport]
newDirs = getDirsNotAlreadyInDatabase(dirHashes)
logger.log("number of dirs to import (i.e. not already in database): %d" % len(newDirs))

if newDirs:
    addDirsToDatabase(newDirs, filesAndPathsToImport)

newPaths = getFilePathsNotAlreadyInDatabase(filesAndPathsToImport)
logger.log("number of paths to import (i.e. not already in database): %d" % len(newPaths))

if newPaths:
    DbQueries.addFilepaths(newPaths)

