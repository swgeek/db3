#!/usr/bin/python

import os
import random



def openRandomFile(filelist):
    filename = None
    while not filename:
        randomFileIndex = int(random.random() * len(filelist))
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

for i in range(3):
    openRandomFile(filelist)

