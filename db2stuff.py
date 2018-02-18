
import sqlite3

import os.path

import ShaHash

import shutil

import DbLogger




def listTables(dbFilePath):
    connection = sqlite3.connect(dbFilePath)
    with connection:
        cursor = connection.cursor()
        command = "SELECT * FROM sqlite_master WHERE type='table';"
        tableList = cursor.execute(command)
        for row in tableList:
            print(row)


def getRowCount(dbFilePath, tableName):
    connection = sqlite3.connect(dbFilePath)
    with connection:
        cursor = connection.cursor()
        command = "SELECT count(*) FROM %s;" % tableName
        count = cursor.execute(command).fetchone()
        print count




def executeSqlQueryReturningMultipleRows(databaseFile, sqlStatement):
    connection = sqlite3.connect(databaseFile)
    connection.text_factory = str
    rows = None
    try:
        with connection: # if do not use with, then have to do "commit" at end
            cursor = connection.cursor()
            cursor.execute(sqlStatement)
            rows = cursor.fetchall()
    except sqlite3.Error, e:
        print "Error %s" % e.args[0]
        exit(1)

    return rows



def getAllDirEntries(databaseFile):
    command = "select * from %s;" % "originalDirectories"
    return executeSqlQueryReturningMultipleRows(databaseFile, command)


def getAllFilesFromDir(databaseFile, dirpathHash):
    command = "select filehash, filename from %s where dirPathHash = '%s';" % ("originalDirectoryForFile", dirpathHash)
    return executeSqlQueryReturningMultipleRows(databaseFile, command)



def copyFiles(filesToExtract, exportDir, depotRoot):
    filesAndNewPaths = {}
    for filehash, filename in filesToExtract:
        newpath = os.path.join(exportDir, filename)
        filesAndNewPaths[filehash] = newpath

    for filehash in filesAndNewPaths:
        sourcePath = os.path.join(depotRoot, filehash[0:2], filehash)
        destinationPath = filesAndNewPaths[filehash]

        if not os.path.isfile(sourcePath):
            logger.log("ERROR: %s does not exist" % sourcePath)
            continue # comment out or get rid of!!
            exit(1)


        if not os.path.exists(os.path.dirname(destinationPath)):
            os.makedirs(os.path.dirname(destinationPath))

        while os.path.exists(destinationPath):
            logger.log("\t%s already exists!" % destinationPath)
            basename, extension = os.path.splitext(destinationPath)
            destinationPath = basename + "_" + extension
            logger.log("\ttrying %s" % destinationPath)

        logger.log("copying %s" % destinationPath)
        shutil.copyfile(sourcePath, destinationPath)


def extractAllFilesFromDir(databaseFile, dirpath, extractDir, depotRoot):
    dirpathHash = ShaHash.HashString(dirpath)
    filelist = getAllFilesFromDir(databaseFile, dirpathHash)
    filesToExtract = []
    for filehash, filename in filelist:
        filesToExtract.append((filehash, filename))

    copyFiles(filesToExtract, extractDir, depotRoot)


logger = DbLogger.dbLogger()
dbFilePath = "/Users/m/oldDepot/listingDb.sqlite"

#listTables(dbFilePath)


#alldirs = getAllDirEntries(dbFilePath)
#for dirhash, dirpath in alldirs:
#    logger.log(dirpath)

dirpath = "I:\\v2\\music\\tosort2"
depotRoot = "/Volumes/wd/objectstore1"
extractDir =  "/Volumes/db/extract"
extractAllFilesFromDir(dbFilePath, dirpath, extractDir, depotRoot)

'''
logger.log("DIRS:")
results = getAllDirEntries(dbFilePath)
dirNames = [x[1] for x in results]

for entry in sorted(dirNames):
    logger.log(entry)
'''


'''
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



'''

'''
(u'table', u'directories', u'directories', 2, u'CREATE TABLE directories (dirPathHash char(40) PRIMARY KEY, dirPath varchar(500))')
(u'table', u'filepaths', u'filepaths', 4, u'CREATE TABLE filepaths (filehash char(40), filename varchar(500), dirPathHash char(40), timestamp integer, PRIMARY KEY (filehash, filename, dirPathHash))')
(u'table', u'files', u'files', 6, u'CREATE TABLE files (filehash char(40) PRIMARY KEY, status varchar(60))')
'''



#getRowCount(dbFilePath, "deletedFiles")