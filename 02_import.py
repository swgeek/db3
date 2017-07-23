# imports files into the db

import os.path
import shutil

import DbLogger
import ShaHash
import settings
import DbQueries


def hashAllFilesInDir(rootDirPath):
    allFilesInDir = {}
    for dirpath, subdirList, subdirFiles in os.walk(rootDirPath):
        for filename in subdirFiles:
            filepath = os.path.join(dirpath, filename)
            filehash = ShaHash.HashFile(filepath)
            filehash = filehash.upper()
            if filehash not in allFilesInDir:
                allFilesInDir[filehash] = []
            allFilesInDir[filehash].append((dirpath, filename))
    return allFilesInDir


def filterFiles(allFiles):
    keep = {}
    skip = []
    for filehash in allFiles:
        for dirpath, filename in allFiles[filehash]:
            if filename.startswith("."):
                skip.append(os.path.join(dirpath, filename))
            else:
                if filehash not in keep:
                    keep[filehash] = []
                keep[filehash].append((dirpath, filename))
    return keep, skip


def getFilesNotAlreadyInDatabase(filehashlist):
    filesInDatabase =  DbQueries.getAllFileshashValues()
    # only want to copy files not in database
    filesToCopy = list(set(filehashlist) - set(filesInDatabase))
    return filesToCopy


def CopyFileIntoDepot(depotRootPath, sourceFilePath, filehash, logger):
        depotSubdir =  filehash[0:2]
        destinationDirPath = os.path.join(depotRootPath, depotSubdir)
        destinationFilePath = os.path.join(depotRootPath, depotSubdir, filehash)

        if not os.path.isdir(destinationDirPath):
            os.mkdir(destinationDirPath)

        # for now always copy, even if file exists. If copy interrupted file may be corrupt, but a reimport will fix
        logger.log("copying %s to %s" % (sourceFilePath, destinationFilePath))
        shutil.copyfile(sourceFilePath, destinationFilePath)


def copyFiles(filesToCopy, allFiles, depotRootPath, logger):
    for filehash in filesToCopy:
        dirpath, filename = allFiles[filehash][0]
        sourceFilePath = os.path.join(dirpath, filename)
        CopyFileIntoDepot(depotRootPath, sourceFilePath, filehash, logger)


def addFilesToFilesTable(filehashList):
    DbQueries.tempAddFilesToFilesTable(filehashList)


def getDirectoryPaths(filesToCopy):
    directoryPaths = []
    for filehash in filesToCopy:
        directoryPaths += filesToCopy[filehash]
    return directoryPaths


def getDirHashes(directories):
    dirhashes = {}
    for dir in directories:
        dirhash = ShaHash.HashString(dir)
        dirhashes[dirhash] = dir
    return dirhashes


def getDirsNotAlreadyInDatabase(dirhashList):
    dirsInDatabase =  DbQueries.getAllDirHashValues()
    dirsToImport = list(set(dirhashList) - set(dirsInDatabase))
    return dirsToImport


def addDirsToDirsTable(dirsToImport, dirHashes):
    dirsToAdd = []
    for dirhash in dirsToImport:
        dirsToAdd.append((dirhash, dirHashes[dirhash]))
    DbQueries.addDirsToDirsTable(dirsToAdd)

def getPathsNotAlreadyInDatabase(dirHashes, filesToImport):
    dirsPaths = {v: k for k, v in dirHashes.iteritems()}

    pathsToImport = []
    for filehash in filesToImport:
        for path in filesToImport[filehash]:
            dirpath = path[0]
            filename = path[1]
            dirhash = dirsPaths[dirpath]
            pathsToImport.append((filehash, filename, dirhash))

    existingPathsInDb = DbQueries.getAllFilePaths()

    filepathsNotInDatabase = list(set(pathsToImport) - set(existingPathsInDb))

    return filepathsNotInDatabase


def addPathsToPathsTable(pathsToImport):
    DbQueries.addPathsToPathsTable(pathsToImport)


def skipDirStart(filesToImport):
    if not settings.skipAtStartOfPath:
        return filesToImport
    importedFiles = {}
    for filehash in filesToImport:
        importedFiles[filehash] = []
        for path in filesToImport[filehash]:
            dirpath = path[0]
            filename = path[1]
            newpath = os.path.relpath(dirpath, settings.skipAtStartOfPath)
            importedFiles[filehash].append((newpath, filename))
    return importedFiles

logger = DbLogger.dbLogger()
dbpath = settings.dbFilePath

allFiles = hashAllFilesInDir(settings.rootDirPath)
logger.log("number of unique files: %d" % len(allFiles.keys()))

filesToImport, filesToSkip = filterFiles(allFiles)
logger.log("number of unique files after filtering: %d" % len(filesToImport.keys()))

logger.log("Skipping files: ")
for entry in filesToSkip:
    logger.log("\t%r" % entry)

filehashlist = filesToImport.keys()
filesToCopy = getFilesNotAlreadyInDatabase(filehashlist)
logger.log("number of unique files to copy (i.e. not already in database): %d" % len(filesToCopy))

copyFiles(filesToCopy, filesToImport, settings.depotRoot, logger)
addFilesToFilesTable(filesToCopy)

filesImported = skipDirStart(filesToImport)

directoryPaths = getDirectoryPaths(filesImported)
directories = set([x[0] for x in directoryPaths])
logger.log("number of directories): %d" % len(directories))

dirHashes = getDirHashes(directories)
dirsToImport = getDirsNotAlreadyInDatabase(dirHashes.keys())
logger.log("number of dirs to import (i.e. not already in database): %d" % len(dirsToImport))

if dirsToImport:
    addDirsToDirsTable(dirsToImport, dirHashes)

pathsToImport = getPathsNotAlreadyInDatabase(dirHashes, filesImported)
logger.log("number of directory Paths): %d" % len(directoryPaths))
logger.log("number of paths to import (i.e. not already in database): %d" % len(pathsToImport))

if pathsToImport:
    addPathsToPathsTable(pathsToImport)


# TODO NEXT
# 4a: option to skip first part of path
# 4b: os independent path?
# 5: report: files skipped, how many copied, how many already there, etc...
# 6: rename vars etc to be more accurate
# 7: clean up
