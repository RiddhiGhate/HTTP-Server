#!/usr/bin/python
import os
fileitem = form['fileToUpload']
if fileitem.fileToUpload:
	fn = os.path.basename(fileitem.fileToUpload)
	open(fn, 'wb').write(fileitem.file.read())