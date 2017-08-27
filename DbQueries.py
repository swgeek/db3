
import sqlite3

import settings
import DbSchema

def executeSqlQueryReturningMultipleRows(sqlStatement):
    connection = sqlite3.connect(settings.databaseFile)
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


def executeMany(sqlStatement, entries):
    connection = sqlite3.connect(settings.databaseFile)
    connection.text_factory = str
    with connection:  # if do not use with, then have to do "commit" at end
        cursor = connection.cursor()
        cursor.executemany(sqlStatement, entries)


def getAllFilehashValues():
    command = "select filehash from %s;" % DbSchema.filesTable
    results = executeSqlQueryReturningMultipleRows(command)
    filehashList = [x[0] for x in results]
    return filehashList


def getAllDirHashValues():
    command = "select dirPathHash from %s;" % DbSchema.directoriesTable
    results = executeSqlQueryReturningMultipleRows(command)
    dirhashList = [x[0] for x in results]
    return dirhashList


def addFiles(filehashList):
    newList = [(x,) for x in filehashList]
    command = "insert into %s (filehash) values (?);" % DbSchema.filesTable
    executeMany(command, newList)


def addDirectories(dirlist):
    command = "insert into %s (dirPathHash, dirPath) values (?, ?);" % DbSchema.directoriesTable
    executeMany(command, dirlist)


def addFilepaths(pathsToImport):
    command = "insert into %s (filehash, filename, dirPathHash, timestamp) values (?, ?, ?, ?);" % DbSchema.filepathsTable
    executeMany(command, pathsToImport)


def getAllFileEntries():
    command = "select * from %s;" % DbSchema.filesTable
    return executeSqlQueryReturningMultipleRows(command)


def getAllDirEntries():
    command = "select * from %s;" % DbSchema.directoriesTable
    return executeSqlQueryReturningMultipleRows(command)


def getAllFilePaths():
    command = "select filehash, filename, dirPathHash from %s;" % DbSchema.filepathsTable
    return executeSqlQueryReturningMultipleRows(command)


def getAllFilePathsWithTimestamps():
    command = "select filehash, filename, dirPathHash, timestamp from %s;" % DbSchema.filepathsTable
    return executeSqlQueryReturningMultipleRows(command)


def getAllDirsAndFiles():
    command = "select dirpath, filename from %s join %s " % (DbSchema.directoriesTable, DbSchema.filepathsTable) \
              + " using (dirPathHash);"
    return executeSqlQueryReturningMultipleRows(command)


def getAllFilesLocationsNamesTimestamps():
    command = "select f.filehash, dirpath, filename, timestamp from " \
               + " %s as f " % DbSchema.filesTable \
               + " join %s as fp " % DbSchema.filepathsTable \
               + " join %s as d " % DbSchema.directoriesTable \
               + " where f.filehash = fp.filehash " \
               + " and fp.dirPathHash = d.dirPathHash;"
    return executeSqlQueryReturningMultipleRows(command)

