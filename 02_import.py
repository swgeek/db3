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


rootDirPath = "/Users/m/dEtc"

logger = DbLogger.dbLogger()
dbpath = settings.dbFilePath

allFiles = hashAllFilesInDir(rootDirPath)
logger.log("number of unique files: %d" % len(allFiles.keys()))

filesToImport, filesToSkip = filterFiles(allFiles)
logger.log("number of unique files after filtering: %d" % len(filesToImport.keys()))

filehashlist = filesToImport.keys()
filesToCopy = getFilesNotAlreadyInDatabase(filehashlist)
logger.log("number of unique files to copy (i.e. not already in database): %d" % len(filesToCopy))

copyFiles(filesToCopy, filesToImport, settings.depotRoot, logger)
addFilesToFilesTable(filesToCopy)

directoryPaths = getDirectoryPaths(filesToImport)
logger.log("number of directory Paths): %d" % len(directoryPaths))

directories = set([x[0] for x in directoryPaths])
logger.log("number of directories): %d" % len(directories))

dirHashes = getDirHashes(directories)
dirsToImport = getDirsNotAlreadyInDatabase(dirHashes.keys())
logger.log("number of dirs to import (i.e. not already in database): %d" % len(dirsToImport))

if dirsToImport:
    addDirsToDirsTable(dirsToImport, dirHashes)

# TODO NEXT
# 4: add dirpaths to db, probably filter first
# 5: report: files skipped, how many copied, how many already there, etc...
# 6: rename vars etc to be more accurate
# 7: clean up
'''
results = DbQueries.getAllDirEntries()
for entry in results:
    logger.log(entry)
'''


'''





db = CoreDb.CoreDb(dbpath)


rootDirPath  = u"I:\\debWorking\\working\\done_pass1"
#rootDirPath  = u"I:\ztempworking"
rootDirPath  = u"I:\\thinkInDepotButCheck"



#excludeList = ["custom.css", "logo.png"]
filehashAndPathList = getFilehashListFromDirPath(rootDirPath, logger)

logger.log("%d files" % len(filehashAndPathList))
count = 0
newFiles = 0
newPaths = 0

depotRootPath1 = "E:\\objectstore1" # should only have through 159 (0x00 to 0x99)
depotRootPath2 = "I:\\objectstore2"  # 161 through 255 (0xA0 to 0XFF)
depotRootPath3 = "I:\\objectstore3"  # new stuff
depotList = [(160, depotRootPath1), (256, depotRootPath2)]

for filehash, dirpath, filename in filehashAndPathList:
	count += 1
	logger.log("%d: %s:%s:%s" % (count, filehash, dirpath, filename))

	filestatus = "notFound"
	fileInfo = miscQueries.getFileInfo(db, filehash)
	if fileInfo:
		filestatus = fileInfo[3]

	if filestatus == "notFound" or filestatus == "deleted":
		logger.log("\tcopying file into depot")
		filepath = os.path.join(dirpath, filename)
		#FileUtils.CopyFileIntoCorrectDepot(depotList, filepath, filehash, logger)
		FileUtils.CopyFileIntoDepot(depotRootPath3, filepath, filehash, logger)
		newFiles += 1
		if not fileInfo:
			filesize = os.path.getsize(filepath)
			logger.log("adding to files table")
			miscQueries.insertFileEntry(db, filehash, filesize, 1)
		else:
			miscQueries.setFileStatus(db, filehash, None)

	newDirPath = dirpath
	#newDirPath = dirpath.replace("F:", "A:")
	dirhash = Sha1HashUtilities.HashString(newDirPath)
	if not miscQueries.checkIfDirhashInDatabase(db, dirhash):
		logger.log("\tnew dir path %s" % newDirPath)
		miscQueries.insertDirHash(db, dirhash, newDirPath)
		newPaths += 1

	if not miscQueries.checkIfFileDirectoryInDatabase(db, filehash, filename, dirhash):
		miscQueries.insertOriginalDir(db, filehash, filename, dirhash)

logger.log("%d new files " % newFiles)
logger.log("%d new paths" % newPaths)


'''
