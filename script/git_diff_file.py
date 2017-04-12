import sys
import subprocess
import re

baseline = sys.argv[1]
current = sys.argv[2]
release = sys.argv[3]
files = []

def remove_duplicates(lines):
	a = []
	for i in lines:
		if i not in a:
			a.append(i)
	return a


if release in 'snapshot':
	ssp_file = '1_modified_sql_full.ssp'
	command_line = "git ls-tree --name-status -r HEAD CUST"
	filestring = subprocess.check_output(command_line, shell=True)
	files = filestring.split('\n')
else:
	#if baseline and current and subprocess.check_output("git tag -l " + baseline, shell=True) and subprocess.check_output("git tag -l " + current, shell=True):
	ssp_file = '1_modified_sql_increment.ssp'
	command_line1 = "git diff-tree -r --name-only  --diff-filter=ACMRTUXB " + baseline + " " + current + " | findstr /B CUST/ 2> nul"
	try:
		filestring1 = subprocess.check_output(command_line1, shell=True, stderr=subprocess.STDOUT) 
	except Exception, e:
		filestring1 = ""
		
	command_line2 = "git diff-tree -r --name-only  --diff-filter=ACMRTUXB " + baseline + " " + current + " | findstr /B VIEW/ 2> nul"
	try:
		filestring2 = subprocess.check_output(command_line2, shell=True, stderr=subprocess.STDOUT) 
	except Exception, e:
		filestring2 = ""
		
	command_line3 = "git diff-tree -r --name-only  --diff-filter=ACMRTUXB " + baseline + " " + current + " | findstr /B OPT_TABLE/ 2> nul"
	try:
		filestring3 = subprocess.check_output(command_line3, shell=True, stderr=subprocess.STDOUT) 
	except Exception, e:
		filestring3 = ""
	
	command_line4 = "git diff-tree -r --name-only  --diff-filter=ACMRTUXB " + baseline + " " + current + " | findstr /B OWCORE/ 2> nul"
	try:
		filestring4 = subprocess.check_output(command_line4, shell=True, stderr=subprocess.STDOUT) 
	except Exception, e:
		filestring4 = ""
	
	fetch_string = filestring1 + filestring2 + filestring3 + filestring4
	files_sorted = fetch_string.split('\n')
	files_sorted.sort()
	files = remove_duplicates(files_sorted)
		
	
print "Opening the file..."
try:
	target = open(ssp_file, 'w') 
except IOError:
	sys.exit("error in opening file")


print 'creating %s file' %ssp_file

string_block1 = []   # used for core spec
string_block2 = []   # used for core body
string_block3 = []   # used for core others
string_block4 = []   # used for opt_table
string_block5 = []   # used for cust spec
string_block6 = []   # used for views spec
string_block7 = []   # used for cust body
string_block8 = []   # used for others

# logic to segrigate files according to its order 
for line in files:
		pattern_owcore = re.compile('^OWCORE/', re.IGNORECASE)
		pattern_table = re.compile('^OPT_TABLE/', re.IGNORECASE)
		pattern_view = re.compile('^VIEW/', re.IGNORECASE)
		pattern_s = re.compile('.*_s.sql', re.IGNORECASE)
		pattern_b = re.compile('.*_b.sql', re.IGNORECASE)
		if '.sql' in line.lower():
			if pattern_owcore.match(line):
				if pattern_s.match(line):
					str = "run " + line
					string_block1.append(str)
				elif pattern_b.match(line):
					str = "run " + line
					string_block2.append(str)
				else:
					str = "run " + line
					string_block3.append(str)
			elif pattern_table.match(line):
				str = "run " + line
				string_block4.append(str)
			elif pattern_s.match(line):
				str = "run " + line
				string_block5.append(str)
			elif pattern_view.match(line):
				str = "run " + line
				string_block6.append(str)
			elif pattern_b.match(line):
				str = "run " + line
				string_block7.append(str)
			else: 
				str = "run " + line
				string_block8.append(str)
				
for str_block in (string_block1, string_block2, string_block3, string_block4, string_block5, string_block6, string_block7, string_block8):
	for str in str_block:
		target.write(str)
		target.write('\n')
target.close()
