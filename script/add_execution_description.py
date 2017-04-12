from urllib2 import Request, urlopen
from jira.client import JIRA
from json import dumps, load
from base64 import b64encode
import os
import argparse
import glob
from requests import post, get

#Version 1.2
#Changes:
#Stacktrace support in message

parser=argparse.ArgumentParser(
    description="""Script to put comment to execution via ZAPI""",
    epilog="""My e-mail: pbuditi@gmail.com""")
parser.add_argument("-i", "--input", help="Input file location. Text file with results query. Examples: 'results\*.txt', '.\test\*.txt'. Default = '.\*.txt'", default=".\*.txt")
parser.add_argument("-d", "--delimeter", help="Delimeter used in query. Default = '|'", default="|")
parser.add_argument("-s", "--skipheader", help="Skip the first line. Use it when query contains header", action="store_true")
parser.add_argument("-p", "--prod", help="Post issue to JIRA prod. Otherwise UAT instance is used", action="store_true")
parser.add_argument("-c", "--credentials", help="JIRA credentials, mandatory. Format: <user>:<password>", required=True)
parser.add_argument("-k", "--key", help="Project key. Default value is 'EP' (EPAM Test)", default="ET")
parser.add_argument("-v", "--version", help="Version name. E.g. '16.3'", default="")
parser.add_argument("-r", "--remove", help="Remove input file after posting the description", action="store_true")
parser.add_argument("-e", "--epamvpn", help=argparse.SUPPRESS, action="store_true")
parser.add_argument("-a", "--attachment", help="Put message as a separate file into execution attachment", action="store_true")

args=parser.parse_args()

inputFileLocation = args.input
delimeter = args.delimeter
ignoreHeader = args.skipheader
isAttachment = args.attachment

# Variables used:
username, password = args.credentials.split(":")
projectName = args.key
versionName = args.version

projectId = 0
versionId = 0

baseURL = ""
if args.prod:
	baseURL = "http://jira.example.com:8081/jira"
else:
	if args.epamvpn:
		baseURL = "http://192.168.1.100:8081/jira"
	else:
		baseURL = "http://172.0.0.1:8081/jira"

getProjectURL = baseURL + "/rest/api/2/project/" + projectName
createCycleURL = baseURL + '/rest/zapi/latest/cycle'
createExecutionURL = baseURL + '/rest/zapi/latest/execution'
attachmentURL = baseURL + '/rest/zapi/latest/attachment'

jira_options={'server': baseURL}
jira=JIRA(options=jira_options,basic_auth=(username,password))

#0. Define the list of comments we are going to update.

#Getting the list of input files	
files = glob.glob(inputFileLocation)
print files

list = []
for file in files:
	with open(file, 'r') as f:
		lineCount = 0
		for line in f:
			if lineCount == 0:
				lineCount = lineCount + 1
				if ignoreHeader:
					continue
			if not line[:1] == delimeter:
				continue
			e, status, run_id, group, code, name, details = line.strip("\n").split(delimeter)
			#0.1 prepare data to update execution comment
			if not (details.isspace() or details == ""):
				stringLine = group + "." + code + delimeter + details
				#print stringLine
				list.append(stringLine)
			#0.2 update issue description
			jqlquery = "project=" + args.key + " AND summary~\'" + group + "." + code + "\'"
			if not (name.isspace() or name == ""):
				issues = jira.search_issues(jqlquery)
				for issue in issues:
					print "----> Updatind issue: " + str(issue)
					issue.update(fields={"description": name})
	if args.remove:
		os.remove(file)

# 'headers' holds information to be sent with the JSON data set
# Initialized with Auth and Content-Type data
# Authorization header uses base64 encoded username and password string
headers = {"Authorization": " Basic " + b64encode(username + ":" + password), "Content-Type": "application/json"}

#1. Define project ID and version ID
projectRequest = Request(getProjectURL, headers=headers)
project_response_body = urlopen(projectRequest)#.read()
projectResponse = load(project_response_body)
projectId = projectResponse['id']

print "Project ID: " + str(projectId)

for version in projectResponse['versions']:
	if version['name']==versionName:
		versionId = version['id']

print "Version ID: " + str(versionId)

#2. Define last Cycle ID
cycleRequest = Request(createCycleURL + "?projectId=" + str(projectId) + "&versionId=" + str(versionId), headers=headers)
cycle_response_body = urlopen(cycleRequest)
cycleResponse = load(cycle_response_body)

maxCycle=0
for cycle in cycleResponse:
	if cycle == "recordsCount":
		continue
	if int(cycle) > maxCycle:
		maxCycle = int(cycle)

print "Last cycleID: " + str(maxCycle)

#3. Get all executions
executionRequest = Request(createExecutionURL + "?projectId=" + str(projectId) + "&versionId=" + str(versionId) + "&cycleId=" + str(maxCycle), headers=headers)
execution_response_body = urlopen(executionRequest)
executionResponse= load(execution_response_body)

for execution in executionResponse['executions']:
	executionId = execution['id']	
	for line in list:
		summary, comment = line.split(delimeter)
		if summary == str(execution['summary']):
			print "Updating execution: " + summary
			
			if isAttachment:
				#write legs to files
				legs = comment.split("~~~")
				for leg in legs:
					#xml = xml.dom.minidom.parseString(leg)
					#pretty_xml_as_string = xml.toprettyxml()					
					fileName = "leg" + str(legs.index(leg) + 1) + ".xml"
				
					print fileName
					#write leg to file
					f = open(fileName,'w')
					f.write(leg) # python will convert \n to os.linesep
					f.close()
					
					# Create file list with file from location provided
					f = open(fileName, 'rb')
					files = {'file':(fileName, f, "multipart/form-data")}
									
					headersP = {"Authorization": "Basic " + b64encode(username + ":" + password), "X-Atlassian-Token": "nocheck", "Accept": "application/json"}
									
					print "Uploading file..."
					print post(attachmentURL + "?entityId=" + str(executionId) + "&entityType=EXECUTION",files=files,headers=headersP)					
					#request = Request(attachmentURL + "?entityId=" + str(executionId) + "&entityType=EXECUTION", data=files, headers=headers)
					#request.get_method = lambda: 'POST'
					#response_body = urlopen(request)
					#executionResponse= load(response_body)

					#Construct request, upload file to JIRA, and print response [200 PASS]
					#post(url,files=files,headers=headers)

					# Close open file
					f.close()					
			else:
				values = "{\"comment\": \"" + comment[-749:] + "\"}"
				request = Request(createExecutionURL + "/" + str(executionId) + "/execute", data=values, headers=headers)
				request.get_method = lambda: 'PUT'
				response_body = urlopen(request)
				executionResponse= load(response_body)
				#print executionResponse
		
