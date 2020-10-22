#!/usr/bin/python

#Syam Krishnan C.R.
#syamcr at gmail dot com


import os
import rpm
import glob
import optparse
import sys
import fnmatch


opt_parser = optparse.OptionParser()
opt_parser.add_option( "-d", dest="dellist_file", help="output file with list of rpm files to be deleted")
opt_parser.add_option( "-k", dest="keeplist_file", help="output file with list of rpm files to be kept")
opt_parser.add_option( "-y", action="store_true", dest="assume_yes", help="answer yes for all questions")
opt_parser.set_defaults( dellist_file=None, keeplist_file=None, assume_yes=False)
options, operands = opt_parser.parse_args()



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
ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)

keep_list   = list()
del_list    = list()
file_list   = list()

for root, dirnames, filenames in os.walk('.'):
  for filename in fnmatch.filter(filenames, '*.rpm'):
      file_list.append(os.path.join(root, filename))

#file_list = glob.glob("*.rpm")
file_list.sort()

for rpm_file in file_list:
	
	h  = readRpmHeader(ts, rpm_file)
	ds = h.dsOfHeader()
	
	current_tuple = (rpm_file, h, ds)
	
	prev_found = 0
	keep = 1
	
	
	for rpm_prev in keep_list:
		if (rpm_prev[1]['name'] == h['name']) and (rpm_prev[1]['arch'] == h['arch']):
			prev_found = 1
			
			#we got a dup
			if rpm.versionCompare(h, rpm_prev[1]) == 1:
				#this is newer than the previously encountered file
				del_list.append(rpm_prev)
				keep_list.remove(rpm_prev)
				keep_list.append(current_tuple)
			else:
				#this is older than the previously encountered file => add to del list
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
	
	if options.dellist_file:
		dellist_file = open(options.dellist_file, "w")
	else:
		dellist_file = None
	
	print 'Files to remove:'
	for entry in del_list:
		print '\t' + entry[0]
		
		if dellist_file:
			dellist_file.write(entry[0] + '\n')
			
	print ''
	
	ok_to_delete = options.assume_yes
	
	if not options.assume_yes:
		s = raw_input('confirm delete[y/n]: ')
		ok_to_delete = (s == 'y')
	
	if ok_to_delete:
		for entry in del_list:
			os.remove(entry[0])
	
else:
	print 'No files to remove'



