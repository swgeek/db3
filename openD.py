#!/usr/bin/python

import os
import random



def openRandomFile(filelist, start=None, end=None):
    filename = None
    if not start:
        start = 0
    if not end:
        end = len(filelist)
    while not filename:
        randomFileIndex = int(random.random() * (end - start) + start)
        filename = filelist[randomFileIndex]
        if not filename.endswith(".txt"):
            filename = None

    #command = "open -a TextEdit %s" % filelist[randomFileIndex]
    command = "open -e %s" % filename
    os.system(command)

dirlist = ["/Users/m/z/d"]

filelist = []
for dir in dirlist:
    for f in os.listdir(dir):
        filepath = os.path.join(dir, f)
        if os.path.isfile(filepath):
            filelist.append(filepath)

filelist.sort()

for i in range(1):
    openRandomFile(filelist)

for i in range(1):
    openRandomFile(filelist, len(filelist) - 50)


