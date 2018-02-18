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

    #command = "open -a TextEdit %s" % filelist[randomFileIndex]
    command = "open '%s'" % filename
    os.system(command)

dirlist = ["/Users/m/z/vids"]

filelist = []
for dir in dirlist:
    for f in os.listdir(dir):
        filepath = os.path.join(dir, f)
        if os.path.isfile(filepath):
            filelist.append(filepath)

filelist.sort()

openRandomFile(filelist)



