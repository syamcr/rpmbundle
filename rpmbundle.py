#!/usr/bin/python

import os
import rpm
import glob


def readRpmHeader(ts, filename):
	""" Read an rpm header. """
	fd = os.open(filename, os.O_RDONLY)
	h = None

	try:
		h = ts.hdrFromFdno(fd)
	except rpm.error, e:
		if str(e) == "public key not available":
			print str(e)
		if str(e) == "public key not trusted":
			print str(e)
		if str(e) == "error reading package header":
			print str(e)
		h = None
	finally:
		os.close(fd)
	
	return h
#------------------------------------------------

ts = rpm.TransactionSet()

keep_list   = list()
del_list    = list()



for rpm_file in glob.glob("*.rpm"):
	
	h  = readRpmHeader(ts, rpm_file)
	ds = h.dsOfHeader()
	
	current_tuple = (rpm_file, h, ds)
	
	prev_found = 0
	keep = 1
	
	
	for rpm_prev in keep_list:
		if (rpm_prev[1]['name'] == h['name']) and (rpm_prev[1]['arch'] == h['arch']):
			prev_found = 1
			#we got a dup
			if rpm_prev[2].EVR() <= ds.EVR():
				#this is newer than the previously encountered file
				del_list.append(rpm_prev)
				keep_list.remove(rpm_prev)
				keep_list.append(current_tuple)
			else:
				#this is older than the previously encountered file => do nothing
				del_list.append(current_tuple)
				
			break
	
	if not prev_found:
		keep_list.append(current_tuple)
#--

if keep_list:
	print 'Files to keep:'
	for entry in keep_list:
		print '\t' + entry[0]
else:
	print 'No files to keep'

print ''


if del_list:
	print 'Files to remove:'
	for entry in del_list:
		print '\t' + entry[0]
	
	print ''
	
	s = raw_input('confirm delete[y/n]: ')
	if s == 'y':
		for entry in del_list:
			os.remove(entry[0])
	
else:
	print 'No files to remove'



