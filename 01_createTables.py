
# for now, directly connecting etc.
# maybe switch to using core db library at some point

# only run first time!

import sqlite3

import DbSchema
import settings

dbFilePath = settings.dbFilePath

'''
uncomment this if creating additional tables after database already created
if not os.path.isfile(dbFilePath):
    print "file %s does not exist! Exiting" % dbFilePath
    exit(1)
'''

connection = sqlite3.connect(dbFilePath)
with connection:  # if do not use with, then have to do "commit" at end
    cursor = connection.cursor()
    createTableCommand = "create table %s (%s);" % (DbSchema.directoriesTable, DbSchema.directoriesSchema)
    cursor.execute(createTableCommand)

    createTableCommand = "create table %s (%s);" % (DbSchema.directoryForFileTable, DbSchema.directoryForFileSchema)
    cursor.execute(createTableCommand)

    createTableCommand = "create table %s (%s);" % (DbSchema.filesTable, DbSchema.filesSchema)
    cursor.execute(createTableCommand)


connection = sqlite3.connect(dbFilePath)
with connection:
    cursor = connection.cursor()
    command = "SELECT * FROM sqlite_master WHERE type='table';"
    tableList = cursor.execute(command)
    for row in tableList:
        print(row)

