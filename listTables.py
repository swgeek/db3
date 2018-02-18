
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



def copyFile(depotRoot, filehash, dirpath, filename, extractDir):
    newDirpath = dirpath.replace(":\\", "/")
    newDirpath = newDirpath.replace("\\", "/")
    newDirpath = os.path.join(extractDir, newDirpath)
    sourcePath = os.path.join(depotRoot, filehash[0:2], filehash)
    newfilepath = os.path.join(newDirpath, filename)
    print sourcePath
    print newDirpath
    print newfilepath

    if not os.path.exists(os.path.dirname(newfilepath)):
        os.makedirs(os.path.dirname(newfilepath))

    while os.path.exists(newfilepath):
        logger.log("\t%s already exists!" % newfilepath)
        basename, extension = os.path.splitext(newfilepath)
        newfilepath = basename + "_" + extension
        logger.log("\ttrying %s" % newfilepath)

    logger.log("copying %s" % newfilepath)
    shutil.copyfile(sourcePath, newfilepath)



def extractAllFilesFromDir(depotRoot, databaseFile, dirpath, extractDir):
    dirpathHash = ShaHash.HashString(dirpath)
    filelist = getAllFilesFromDir(databaseFile, dirpathHash)
    for filehash, filename in filelist:
        filepath = dirpath + filename
        print "copying %s" % filepath
        copyFile(depotRoot, filehash, dirpath, filename, extractDir)

    print len(filelist)



logger = DbLogger.dbLogger()
dbFilePath = "/Users/m/dbV1/listingDb.sqlite"
depotRoot = "/Volumes/wd/objectstore1"
#alldirs = getAllDirEntries(dbFilePath)
#for dirhash, dirpath in alldirs:
#    logger.log(dirpath)


dirpath = "F:\\_moved\\fromPhone"
print dirpath
extractAllFilesFromDir(depotRoot, dbFilePath, dirpath, "/Users/m/export")

'''

F:\_moved\fromPhone
F:\iphoneFromCorruptDrive

A:\fromAir_20151012
D:\fromSeagate\fromMyMac20150218\toMove


'''

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

(u'table', u'sqlite_sequence', u'sqlite_sequence', 3, u'CREATE TABLE sqlite_sequence(name,seq)')
0 count, probably not used any more

(u'table', u'fileListing', u'fileListing', 4, u'CREATE TABLE fileListing (filehash char(40), depotId INTEGER,
           filesize int, FOREIGN KEY (depotId) REFERENCES objectStores(depotId), PRIMARY KEY (filehash, depotId))')
1800137 count
tells me which depot each file is in, don't think I used this any more. Don't need it any more anyway...

(u'table', u'files', u'files', 693811, u'CREATE TABLE files (filehash char(40) PRIMARY KEY, filesize int, status varchar(60))')
1817239 count, think replaced by filesV2 but not 100% sure

(u'table', u'oldStatus', u'oldStatus', 1417612, u'CREATE TABLE oldStatus (filehash char(40) PRIMARY KEY, oldStatus varchar(60))')
1800205 count, obviously status in older depot version, so know if previously deleted etc.. Not necessary.

(u'table', u'oldFileLink', u'oldFileLink', 1618410, u'CREATE TABLE oldFileLink (filehash char(40) PRIMARY KEY, linkFileHash char(40))')
6213 count. Weird table, think links to older version of file if replaced, e.g. photoshop file resized. Not necessary

(u'table', u'originalDirectories', u'originalDirectories', 1619298, u'CREATE TABLE originalDirectories (dirPathHash char(40) PRIMARY KEY, dirPath varchar(500))')
73141 count. Need this, directory listing

(u'table', u'originalDirectoryForFile', u'originalDirectoryForFile', 1679478, u'CREATE TABLE originalDirectoryForFile (filehash char(40), filename varchar(500), dirPathHash char(40), PRIMARY KEY (filehash, filename, dirPathHash))')
2536340 count. Need this, maps file to directory with name.

(u'table', u'subDirsTable', u'subDirsTable', 2900502, u'CREATE TABLE subDirsTable (dirPathHash char(40), subDirPathHash char(40), PRIMARY KEY (dirPathHash, subDirPathHash))')
264753 count. Don't think I need this any more, used for detecting duplicate subdir trees etc.
Why is this larger than original dirs? Unless lots of dirs only containing dirs?

(u'table', u'toKeepForNow', u'toKeepForNow', 2952747, u'CREATE TABLE toKeepForNow (filehash char(40) PRIMARY KEY)')
14 count. Ugh, no idea why I have this. Guess sorted, keeping for now but not in files?

(u'table', u'toDelete', u'toDelete', 2953246, u'CREATE TABLE toDelete (filehash char(40) PRIMARY KEY, oldStatus varchar(60), filesize int, filenames varchar(500), directories varchar(500))')
0 count, don't need any more

(u'table', u'primaryFiles', u'primaryFiles', 2984869, u'CREATE TABLE primaryFiles (filehash char(40) PRIMARY KEY)')
1793236 count. No idea what this means. How is primaryFiles different from regular files?? Maybe contains everything??


(u'table', u'filesV2', u'filesV2', 105234, u'CREATE TABLE filesV2 (filehash char(40) PRIMARY KEY, filesize int, primaryLocation int, status varchar(60))')
1126287 count. Should be an entry for each file, but why is primaryFiles larger than this?

(u'table', u'deletedFiles', u'deletedFiles', 261159, u'CREATE TABLE deletedFiles (filehash char(40) PRIMARY KEY)')
658610 count. Self explanatory.

'''

#getRowCount(dbFilePath, "deletedFiles")