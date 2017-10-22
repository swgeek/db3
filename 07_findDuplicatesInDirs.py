#!/usr/bin/python

# given a list of directories it finds all duplicate files

import argparse
import os

import DbLogger
import ShaHash

# simple filter, remove dirs starting with "."
# not removing files yet, may add that if needed
def getFileList(rootDirPath):
    fileList = []
    skippedDirs = []
    skippedFiles = []
    for dirpath, subdirs, files in os.walk(rootDirPath):
        #make copy of subdirs before iterating as will be modifying subdirs
        subdirsCopy = subdirs[:]
        for dirname in subdirsCopy:
            if dirname.startswith(".") or dirname.endswith(".lrdata"):
                subdirpath = os.path.join(dirpath, dirname)
                skippedDirs.append(subdirpath)
                subdirs.remove(dirname)
        for filename in files:
            filepath = os.path.join(dirpath, filename)
            if filename.startswith("."):
                skippedFiles.append(filepath)
            else:
                fileList.append(filepath)
    return fileList, skippedDirs, skippedFiles


parser = argparse.ArgumentParser()
parser.add_argument("directories", nargs="*", help="directories")
parser.add_argument("-d", action="store_true", help="delete duplicates, keep first filepath (sorted)")
args = parser.parse_args()
directories = args.directories
deleteDuplicates = args.d

logger = DbLogger.dbLogger()

logger.log("delete duplicates: %r" % deleteDuplicates)
logger.log("directories to check:")
for dir in directories:
    logger.log("\t%s\n\n" % dir)

allFilepaths = []
for dir in directories:
    filelist, skippedDirs, skippedFiles = getFileList(dir)
    for entry in skippedDirs:
        logger.log("skipping dir %s" % entry)
    for entry in skippedFiles:
        logger.log("skipping file %s" % entry)
    allFilepaths += filelist

allUniqueFilepaths = set(allFilepaths)

filehashToPathMapping = {}

for filepath in allUniqueFilepaths:
    filehash = ShaHash.HashFile(filepath)
    filehash = filehash.upper()
    if not filehash in filehashToPathMapping:
        filehashToPathMapping[filehash] = []
    filehashToPathMapping[filehash].append(filepath)

logger.log("\n\nDuplicates:")
for filehash in filehashToPathMapping:
    if len(filehashToPathMapping[filehash]) > 1:
        filehashToPathMapping[filehash].sort()
        logger.log(filehashToPathMapping[filehash][0])
        for filepath in filehashToPathMapping[filehash][1:]:
            if filepath.startswith("/Users/v724660/github"):
                continue
            if deleteDuplicates:
                logger.log("\tdeleting %s" % filepath)
                os.remove(filepath)
            else:
                logger.log("\t%s" % filepath)
