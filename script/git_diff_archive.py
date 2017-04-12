###############################################################################
###### This script will diff between two tags and and archives it
######  Usage: ./create_archive.py 16.4.DEV.INITIAL 16.4.RC2 filename.zip
######  Author : Pradeep Kumar Buditi
################################################################################
import zipfile
import sys
import subprocess
import re
import os
import os.path

baseline = sys.argv[1]
current = sys.argv[2]
archive_name = current + '.zip'
release = sys.argv[3] 
runbook_version = sys.argv[4]     # Runbook version. If empty it will consider all runbooks    
    # expected snapshot for production baseline. empty urgument will be considered as increment
files = []
files_string = ''
	
def remove_duplicates(lines):
	a = []
	for i in lines:
		if i not in a:
			a.append(i)
	return a

if release in 'snapshot':
	ssp_file = '1_modified_sql_full.ssp'
	directories = os.listdir('.')
	for dir in directories:
		if dir not in 'CONFIG':
			fetch_command = "git ls-tree --name-status -r HEAD " + dir
			fetch_string = subprocess.check_output(fetch_command, shell=True) 
			files_string = files_string + fetch_string
	files = files_string.split('\n')
else:
	ssp_file = '1_modified_sql_increment.ssp'
	
	fetch_commands = [
		"git diff-tree -r --name-only  --diff-filter=ACMRTUXB " + baseline + " " + current,
		"git ls-tree --name-status -r HEAD POST_CC_SCRIPT",
		"git ls-tree --name-status -r HEAD DML",
		"git ls-files RUNBOOK",
		"git ls-files --others --exclude-standard RUNBOOK",
		"git ls-files --others --exclude-standard deployment",
		"git ls-files --others --exclude-standard . "
	]
	
	fetch_output = []	
	for fetch_command in fetch_commands:
		fetch_string = subprocess.check_output(fetch_command, shell=True)
		fetch_string_split = fetch_string.split('\n')
		fetch_output += fetch_string_split
	
	fetch_output.sort()
	files = remove_duplicates(fetch_output)
	
    
#filepaths = re.sub("////","\\\\",files)

print 'creating archive ' + archive_name
zf = zipfile.ZipFile(archive_name, mode='w')
try:
    zf.write('README.md')
finally:
    zf.close()

print 'appending to the archive'
zf = zipfile.ZipFile(archive_name, mode='a')

try:
	for file in files:
		filepath = file.replace("/","\\")
		pattern_runbook = re.compile('^RUNBOOK')
		pattern_config = re.compile('^CONFIG')
#		pattern_version = re.compile(runbook_version)
		pattern_dml = re.compile('^DML')
		pattern_postcc = re.compile('^POST_CC_SCRIPT')
		if pattern_runbook.match(filepath) or pattern_config.match(filepath) or pattern_dml.match(filepath)  or pattern_postcc.match(filepath):
			if runbook_version !='' and runbook_version in filepath:
				print 'include - ' + filepath
				zf.write(filepath)
			else:
				print 'exclude - ' + filepath
		elif filepath != '' and "DATA_MART" not in filepath :
			print 'include - ' + filepath
			zf.write(filepath)
		else:
			print 'unknown - ' + filepath
finally:
	zf.close()
