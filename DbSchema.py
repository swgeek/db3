

directoryForFileTable = "directoryForFile"
directoryForFileSchema = "filehash char(40), filename varchar(500), dirPathHash char(40), PRIMARY KEY (filehash, filename, dirPathHash)"

directoriesTable = "directories"
directoriesSchema = "dirPathHash char(40) PRIMARY KEY, dirPath varchar(500)"

filesTable = "files"
filesSchema = "filehash char(40) PRIMARY KEY, filesize int, status varchar(60)"


