
import sqlite3

import settings
import DbSchema

def executeSqlQueryReturningMultipleRows(sqlStatement):
    connection = sqlite3.connect(settings.dbFilePath)
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


def executeManyNonQuery(sqlStatement, entries):
    connection = sqlite3.connect(settings.dbFilePath)
    connection.text_factory = str
    with connection:  # if do not use with, then have to do "commit" at end
        cursor = connection.cursor()
        cursor.executemany(sqlStatement, entries)


def getAllFileshashValues():
    command = "select filehash from %s;" % DbSchema.filesTable
    results = executeSqlQueryReturningMultipleRows(command)
    filehashList = [x[0] for x in results]
    return filehashList


def getAllDirHashValues():
    command = "select dirPathHash from %s;" % DbSchema.directoriesTable
    results = executeSqlQueryReturningMultipleRows(command)
    dirhashList = [x[0] for x in results]
    return dirhashList


# FIGURE OUT HOW TO DO THIS!
def addFilesToFilesTable(filehashList):
    newList = [(x) for x in filehashList]
    command = "insert into %s (filehash) values (?);" % DbSchema.filesTable
    executeManyNonQuery(command, newList)


def tempAddFilesToFilesTable(filehashList):
    connection = sqlite3.connect(settings.dbFilePath)
    connection.text_factory = str
    try:
        with connection:  # if do not use with, then have to do "commit" at end
            cursor = connection.cursor()
            for filehash in filehashList:
                sqlStatement = "insert into %s (filehash) values (\"%s\");" % (DbSchema.filesTable, filehash)
                cursor.execute(sqlStatement)
    except sqlite3.Error, e:
        print "Error %s" % e.args[0]
        exit(1)



# FIGURE OUT HOW TO DO THIS!
def addDirsToDirsTable(dirlist):
    command = "insert into %s (dirPathHash, dirPath) values (?, ?);" % DbSchema.directoriesTable
    executeManyNonQuery(command, dirlist)



def getAllFileEntries():
    command = "select * from %s;" % DbSchema.filesTable
    return executeSqlQueryReturningMultipleRows(command)


def getAllDirEntries():
    command = "select * from %s;" % DbSchema.directoriesTable
    return executeSqlQueryReturningMultipleRows(command)

