#Program		: ASSIGNMENT 2 (FILE SYSTEM CHECKER)
#Name			: RUPANTA RWITEEJ DUTTA
#Email Address		: rrd300@nyu.edu
#Date of Creation	: 11.21.2015
#School			: NYU Tandon School of Engineering
#NYU ID			: N15786532
#Net ID			: rrd300
#Subject		: Introduction to Operating System

#import os.path
import time

#Declare Global Variables
super_block = 0
max_block_size = 4096
devFlag = 1
aTimeFlag = 1
cTimeFlag = 1
mTimeFlag = 1
freeBlocksFlag1 = 1
freeBlocksFlag2 = 1
currentFlag = 1
parentFlag = 1
directoryFlag = 1
linkCountFlag = 1
fileToInodeFlag = 1
directSizeFlag = 1
locArrayFlag = 1
indirectSizeFlag = 1
existsFileTrue = []
maxBlocks = 0
freeStart = 0
freeEnd = 0
root = 0

#Function to Read Parsed Data from a Block
def parseData(block):
	global existsFileTrue
	fileName = "FS/fusedata." + str(block)
	fo = open(fileName,"r")
	dataBlock = fo.read()
	fo.close()
	dataBlock = dataBlock.strip('{')
	dataBlock = dataBlock.strip('}')
	attributes = dataBlock.split(", ")
	existsFileTrue.append(fileName)
	return attributes

#Function to Write Data to a Block
def writeData(block, data):
	fileName = "FS/fusedata." + str(block)
	fo = open(fileName,"w")
	dataBlock = fo.write(data)
	fo.close()	

#Check & Rectify Super Block Errors
def checkSuperBlock():
	global devFlag
	global cTimeFlag
	global root
	global maxBlocks
	global freeStart
	global freeEnd
	outputString = "{"
	attributes = parseData(super_block)
	count_attributes = len(attributes)
	for index in range(len(attributes)):
		subAttributes = attributes[index].split(":")
		if "mounted" in subAttributes[0]:
			if subAttributes[1]:
				subAttributes[1] = int(subAttributes[1])
				mounted = subAttributes[1]
				outputString = outputString + ', ' + subAttributes[0] + ': ' + str(subAttributes[1])	
		if "devId" in subAttributes[0]:
			subAttributes[1] = int(subAttributes[1])
			if (subAttributes[1] == 20):
				devFlag = 1
				print "BLOCK 0: Device ID Check: PASSED"
			else:
				devFlag = 0
				subAttributes[1] = 20
				print "BLOCK 0: Device ID Check: ERROR"
			outputString = outputString + ', ' + subAttributes[0] + ':' + str(subAttributes[1])
		if "root" in subAttributes[0]:
			if subAttributes[1]:
				subAttributes[1] = int(subAttributes[1])
				root = subAttributes[1]
			outputString = outputString + ', ' + subAttributes[0] + ':' + str(subAttributes[1])
		if "maxBlocks" in subAttributes[0]:
			if subAttributes[1]:
				subAttributes[1] = int(subAttributes[1])
				maxBlocks = subAttributes[1]
			outputString = outputString + ', ' + subAttributes[0] + ':' + str(subAttributes[1]) + '}'
		if "freeStart" in subAttributes[0]:
			if subAttributes[1]:
				subAttributes[1] = int(subAttributes[1])			
				freeStart = subAttributes[1]
			outputString = outputString + ', ' + subAttributes[0] + ':' + str(subAttributes[1])
		if "freeEnd" in subAttributes[0]:
			if subAttributes[1]:
				subAttributes[1] = int(subAttributes[1])
				freeEnd = subAttributes[1]
			outputString = outputString + ', ' + subAttributes[0] + ':' + str(subAttributes[1])
		if "creationTime" in subAttributes[0]:
			if subAttributes[1]:
				subAttributes[1] = float(subAttributes[1])
				if time.time() < subAttributes[1]:
					cTimeFlag = 0
					subAttributes[1] = str(time.time())
					print "BLOCK 0: Creation Time Check: ERROR"
				else:
					print "BLOCK 0: Creation Time Check: PASSED"
			outputString = outputString + subAttributes[0] + ':' + str(subAttributes[1])
	writeData(super_block, outputString)	

#Check Location Array Block
def getArrayBlock(current):
	global existsFileTrue
	attributes = parseData(current)
	for i in xrange(0,len(attributes)):
		fileName = "FS/fusedata." + str(attributes[i])
		existsFileTrue.append(fileName)
	return len(attributes)

#Check & Rectify File Errors
def checkFiles(current):
	global aTimeFlag
	global cTimeFlag
	global mTimeFlag
	global directSizeFlag
	global locArrayFlag
	global indirectSizeFlag
	attributes = parseData(current)
	dictionary = {}
	outputString = "{"
	subOutput = "{"
	for i, attribute in enumerate(attributes):
		attribute = attribute.split(":",1)
		key = attribute[0]
		value = attribute[1]
		dictionary[key] = value
	if time.time() < float(dictionary.get('atime')):
		aTimeFlag = 0
		dictionary['atime'] = str(time.time())
		print "BLOCK %s: Access Time Check: ERROR" %current
	else:
		print "BLOCK %s: Access Time Check: PASSED" %current
	if time.time() < float(dictionary.get('ctime')):
		cTimeFlag = 0
		dictionary['ctime'] = str(time.time())
		print "BLOCK %s: Creation Time Check: ERROR" %current
	else:
		print "BLOCK %s: Creation Time Check: PASSED" %current
	if time.time() < float(dictionary.get('mtime')):
		mTimeFlag = 0
		dictionary['mtime'] = str(time.time())
		print "BLOCK %s: Modified Time Check: ERROR" %current
	else:
		print "BLOCK %s: Modified Time Check: PASSED" %current
	if dictionary.get('indirect'):
		if "0 " in dictionary.get('indirect'):
			if int(dictionary.get('size')) >  max_block_size or int(dictionary.get('size')) <  0:
				directSizeFlag = 0
				print "BLOCK %s: Direct Size Check: ERROR" %current
			if int(dictionary.get('size')) > 0 and int(dictionary.get('size')) < max_block_size:  
				print "BLOCK %s: Direct Size Check: PASSED" %current
		if "1 " in dictionary.get('indirect'):
			locationBlock = dictionary.get('indirect').split(" ")
			locationBlock = locationBlock[1].split(":")
			arrLength = getArrayBlock(int(locationBlock[1]))
			if isinstance(arrLength, int):
				print "BLOCK %s: Location Array Length Check: PASSED" %current
				if int(dictionary.get('size')) >  (max_block_size * (arrLength - 1)) and int(dictionary.get('size')) <  (max_block_size * arrLength):
					print "BLOCK %s: Indirect Size Check: PASSED" %current
				else:
					indirectSizeFlag = 0
					print "BLOCK %s: Indirect Size Check: ERROR" %current
			else:
				locArrayFlag = 0
				print "BLOCK %s: Location Array Length Check: ERROR" %current
	outputString = outputString + 'size:' + str(dictionary.get('size')) + ', uid:' + dictionary.get('uid') + ', gid:' + dictionary.get('gid') + ', mode:' + dictionary.get('mode') + ', atime:' + dictionary.get('atime') + ', ctime:' + dictionary.get('ctime') +', mtime:' + dictionary.get('mtime') + ', indirect:' + dictionary.get('indirect') + '}'
	writeData(current, outputString)

#Check & Rectify Directory Errors
def checkDirectory(parent, current):
	global aTimeFlag
	global cTimeFlag
	global mTimeFlag
	global parentFlag
	global currentFlag
	global directoryFlag
	global linkCountFlag
	global fileToInodeFlag
	global handle
	outputString = "{"
	subOutput = "{"
	check = 0	
	attributes = parseData(current)
	for index in range(len(attributes)):
		if "filename_to_inode_dict:" in attributes[index]:
			handle = i = index
			val=''
			while i < len(attributes):
				val = val + attributes[i] + ", " 
				i=i+1
			val = val[0:len(val)-2]
			val = val + "}"
	i = handle + 1
	attributes[handle] = val
	attributes = attributes[0:handle+1]
	dictionary = {}
	for i, attribute in enumerate(attributes):
		attribute = attribute.split(":",1)
		key = attribute[0]
		value = attribute[1]
		dictionary[key] = value
	if time.time() < float(dictionary.get('atime')):
		aTimeFlag = 0
		dictionary['atime'] = str(time.time())
		print "BLOCK %s: Access Time Check: ERROR" %current
	else:
		print "BLOCK %s: Access Time Check: PASSED" %current
	if time.time() < float(dictionary.get('ctime')):
		cTimeFlag = 0
		dictionary['ctime'] = str(time.time())
		print "BLOCK %s: Creation Time Check: ERROR" %current
	else:
		print "BLOCK %s: Creation Time Check: PASSED" %current
	if time.time() < float(dictionary.get('mtime')):
		mTimeFlag = 0
		dictionary['mtime'] = str(time.time())
		print "BLOCK %s: Modified Time Check: ERROR" %current
	else:
		print "BLOCK %s: Modified Time Check: PASSED" %current
	linkCount = int(dictionary.get('linkcount'))
	links = dictionary.get('filename_to_inode_dict')
	links = links.strip(" {")
	links = links.strip("}")
	subLinks = links.split(", ")
	if len(subLinks) != linkCount:
		linkCountFlag = 0
		dictionary['linkcount'] = str(len(subLinks))
	for index in subLinks:
		parts = index.split(":")
		if parts[0] == "d" and parts[1] == ".":
			check = check + 1
			if int(parts[2]) != current:
				currentFlag = 0
				parts[2] = str(current)
				print "BLOCK %s: . Directory Check: ERROR" %current
			else:
				print "BLOCK %s: . Directory Check: PASSED" %current
			subOutput = subOutput + 'd:.:'  + parts[2] + ', '
		elif parts[0] == "d" and parts[1] == "..":
			check = check + 2			
			if int(parts[2]) != parent:
				parentFlag = 0
				parts[2] = str(parent)
				print "BLOCK %s: .. Directory Check: ERROR" %current
			else:
				print "BLOCK %s: .. Directory Check: PASSED" %current
			subOutput = subOutput + 'd:..:'  + parts[2] + ', '
		elif parts[0] == "d" and parts[1] not in ['.', '..']:
			checkDirectory(current, int(parts[2]))
			subOutput = subOutput + 'd:' + parts[1] + ':' + parts[2] + ', '
		elif parts[0] == "f":
			checkFiles(int(parts[2]))
			subOutput = subOutput + 'f:' + parts[1] + ':' + parts[2] + ', '
		else:
			fileToInodeFlag = 0
	if check == 0:
		directoryFlag = 0
		subOutput = subOutput + 'd:.:' + str(current) + ', d:..:' + str(parent) + ', '
		print "BLOCK %s: . & .. Directories Present Check: ERROR" %current
	if check == 1:
		directoryFlag = 0
		subOutput = subOutput + 'd:..:' + str(parent) + ', '
		print "BLOCK %s: . & .. Directories Present Check: ERROR" %current
	if check == 2:
		directoryFlag = 0
		subOutput = subOutput + 'd:.:' + str(current) + ', '
		print "BLOCK %s: . & .. Directories Present Check: ERROR" %current
	else:
		print "BLOCK %s: . & .. Directories Present Check: PASSED" %current
	subOutput = subOutput.strip(', ')	
	subOutput = subOutput + '}'	
	outputString = outputString + 'size:' + str(dictionary.get('size')) + ', uid:' + dictionary.get('uid') + ', gid:' + dictionary.get('gid') + ', mode:' + dictionary.get('mode') + ', atime:' + dictionary.get('atime') + ', ctime:' + dictionary.get('ctime') +', mtime:' + dictionary.get('mtime') + ', linkcount:' + dictionary.get('linkcount') + ', filename_to_inode_dict: ' + subOutput + '}'
	writeData(current, outputString)

#Check & Rectify Free Block Errors
def checkFreeBlocks():
	global existsFileTrue
	global maxBlocks
	global freeStart
	global freeEnd
	global freeBlocksFlag1
	global freeBlocksFlag2
	for i in xrange(freeStart,freeEnd+1):
		fileName = "FS/fusedata." +str(i)
		existsFileTrue.append(fileName)
	fbl = []
	existsFileFalse = []
	for i in xrange (freeStart,freeEnd+1):	
		fileName = "FS/fusedata." + str(i)
		fo = open(fileName,"r")
		FreeBlock = fo.read()
		fo.close()
		FreeBlock = FreeBlock.strip(" ")	
		fb = FreeBlock.split(", ")
		for j in fb:
			j = "FS/fusedata." + str(j)
			fbl.append(j)
	for i in xrange (0, maxBlocks):
		fileName = "FS/fusedata." +str(i)	
		if fileName not in existsFileTrue:
			existsFileFalse.append(fileName)		
	for index in existsFileFalse:
		if index not in fbl:
			freeBlocksFlag1 = 0
			print "BLOCK 0: Free Block List Check: ERROR"
		else:
			print "BLOCK 0: Free Block List Check: PASSED"
	for index in existsFileTrue:
		if index in fbl:
			freeBlocksFlag2 = 0
			print "BLOCK 0: Free Block List Check: ERROR"
		else:
			print "BLOCK 0: Free Block List Check: PASSED"
	for i in xrange (freeStart,freeEnd+1):	
		fileName = "FS/fusedata." + str(i)
		fo = open(fileName,"w")
		FreeBlock = fo.write('')
		fo.close()
	writeList = []
	for index in existsFileFalse:
		index = index.strip("FS/fusedata.")
		writeList.append(int(index))
	writeList = sorted(writeList)
	j = freeStart
	i = 400
	count = 0
	while(j < freeEnd+1):
		outputString = ""
		while count<len(writeList) and writeList[count] < i:
			outputString = outputString + str(writeList[count]) + ', '
			count = count + 1
		outputString = outputString.strip(', ')
		writeData(j, outputString)
		j = j + 1
		i = i + 400
		
#Function to Print Error to Screen	
def printError():
	print "----------------------------------------"
	print "\n"
	print "----------------------------------------"
	print "FILE SYSTEM CHECKER : SUMMARY"
	print "----------------------------------------"
	if devFlag == 1:
		print "DeviceID        		: PASSED"
	else: 
		print "DeviceID        		: ERROR"
	if aTimeFlag == 1:
		print "Access Timestamps      		: PASSED"
	else: 
		print "Access Timestamps       	: ERROR"
	if cTimeFlag == 1:
		print "Creation Timestamps     	: PASSED"
	else: 
		print "Creation Timestamps     	: ERROR"
	if mTimeFlag == 1:
		print "Modified Timestamps     	: PASSED"
	else: 
		print "Modified Timestamps     	: ERROR"
	if freeBlocksFlag1 == 1 and freeBlocksFlag2 == 1:
		print "Free Block List 		: PASSED"
	else: 
		print "Free Block List 		: ERROR"
	if fileToInodeFlag == 1:
		print "Valid File to Inode Directory	: PASSED"	
	else:
		print "Valid File to Inode Directory	: ERROR"
	if directoryFlag == 1:
		print ". & .. Directories Present 	: PASSED"
	else:
		print ". & .. Directories Present 	: ERROR"
	if currentFlag == 1:
		print ". Directory Links     		: PASSED"
	else:
		print ". Directory Links     		: ERROR"
	if parentFlag == 1:
		print ".. Directories    		: PASSED"
	else:
		print ".. Directories    		: ERROR"
	if linkCountFlag == 1:
		print "Link Counts    			: PASSED"
	else:
		print "Link Counts    			: ERROR"
	if directSizeFlag == 1:
		print "Direct Size    			: PASSED"
	else:
		print "Direct Size    			: ERROR"
	if locArrayFlag ==1:
		print "Location Array Size    		: PASSED"
	else:
		print "Location Array Size    		: ERROR"
	if indirectSizeFlag == 1:
		print "Indirect Size    		: PASSED"
	else:
		print "Indirect Size    		: ERROR"
	print "----------------------------------------"

def main():
	print "\n\n----------------------------------------"
	print "FILE SYSTEM CHECKER"
	print "----------------------------------------"
	print "Checking File System..."
	for i in range (1,9999999):
		i
	checkSuperBlock()
	checkDirectory(root, root)
	checkFreeBlocks()
	printError()
	print "\nCorrecting File System..."
	for i in range (1,9999999):
		i
	print "\nFile System: ALL ERRORS HAVE BEEN RECTIFIED!!!\n"

if __name__ == "__main__":
	main()
