from urllib2 import Request, urlopen
from base64 import b64encode
from json import dumps, load
import argparse
import requests

#Version 1.1
#Changes:
#Removed hardcoded space key
#Impemented assertions during script run
#TODO:
#Test script on real data
#Update default parent page id or make it required (optional)

parser=argparse.ArgumentParser(
    description="""Script to get Issues mansioned in Pull Requests and add it to the confluence page""",
    epilog="""My e-mail: pbuditi@gmail.com""")

parser.add_argument("-n", "--name", help="Release name", default="Release_01", required=True)
parser.add_argument("-p", "--pullrequest", help="Pull-request ID", default="264", required=True)
parser.add_argument("-i", "--id", help="Parent Confluence page ID", default="23068680")
parser.add_argument("-c", "--credentials", help="JIRA credentials, mandatory. Format: <user>:<password>", required=True)
parser.add_argument("-u", "--uat", help="Use UAT Stash and Confluence instance. Otherwise Production instances are used", action="store_true")
parser.add_argument("-e", "--epamvpn", help=argparse.SUPPRESS, action="store_true")

args=parser.parse_args()

baseURL = ""
if not args.uat:
	baseURL = "http://jira.example.com"
else:
	if args.epamvpn:
		baseURL = "http://192.168.1.100"
	else:
		baseURL = "http://172.0.0.1"

getPullRequestIssuesURL = baseURL + ":7991/stash/rest/jira/1.0/projects/NI/repos/emirates-nbd/pull-requests/" + args.pullrequest + "/issues"
postPageURL =  baseURL + ":8091/confluence/rest/api/content/"
putPageURL =  baseURL + ":8091/confluence/rest/api/content/" + args.id
getPageURL = baseURL + ":8091/confluence/rest/api/content/" + args.id + "?expand=body.storage,version,space"

# 'headers' holds information to be sent with the JSON data set
# Initialized with Auth and Content-Type data
# Authorization header uses base64 encoded username and password string
username, password = args.credentials.split(":")
headers = {"Authorization": " Basic " + b64encode(username + ":" + password), "Content-Type": "application/json"}

#1. Get JSON with Issues based on Pull-request ID from Stash
print "Requesting issues related to Pull-request " + args.pullrequest
getPullRequestIssuesRequest = Request(getPullRequestIssuesURL, headers=headers)
response_body = urlopen(getPullRequestIssuesRequest)#.read()
getPullRequestIssuesResponse = load(response_body)

#2. Get list of issues and form a JQL String
JQLString = "issuekey in ("
isFirstIssue = True
for issue in getPullRequestIssuesResponse:
	issueKey = issue['key']
	if not isFirstIssue:
		JQLString = JQLString + ", "
	JQLString = JQLString + str(issueKey)
	isFirstIssue = False
JQLString = JQLString + ")"
print "JQL query is " + JQLString
assert not isFirstIssue, ("No issues found for pull-request " + args.pullrequest)


#3. Get existing content of Parent page
print "Getting parent page details"
getPageRequest = Request(getPageURL, headers=headers)
response_body = urlopen(getPageRequest)
getPageResponse = load(response_body)

title = getPageResponse['title']

version = getPageResponse['version']['number']
version = version + 1

space = getPageResponse['space']['key']
print "New parent page version version value will be " + str(version) + ". Title remains " + title + ". Space remains " + space

storage = getPageResponse['body']['storage']['value']

storageIncrement = "<h2>" + args.name + "</h2><p><ac:structured-macro ac:name=\"include\" ac:schema-version=\"1\"><ac:parameter ac:name=\"\"><ac:link><ri:page ri:content-title=\"" + args.name + "\"/></ac:link></ac:parameter></ac:structured-macro></p>"

storage = storageIncrement + storage


#4. POST Release notes Page to Confluence
print "Add new Release notes page to parent page"
data ={
	"type":"page",
	"title":args.name,
	"ancestors": [{
		"id":args.id
	}],
	"space": {
		"key":space
	},
	"body": {
		"storage": {
			"value":"<ac:structured-macro ac:name=\"jira\" ac:schema-version=\"1\"><ac:parameter ac:name=\"server\">Network JIRA</ac:parameter><ac:parameter ac:name=\"columns\">key,summary,priority,assignee,reporter</ac:parameter><ac:parameter ac:name=\"maximumIssues\">50</ac:parameter><ac:parameter ac:name=\"jqlQuery\">" + JQLString + "</ac:parameter><ac:parameter ac:name=\"serverId\">9bae4c5a-1b9e-37cc-8b74-cc24dde9c1f5</ac:parameter></ac:structured-macro>",
			"representation":"storage"
			}
	}
}
response = requests.post(postPageURL, data=dumps(data), headers=headers)
print response
assert str(response) == "<Response [200]>", "Failed to add new Confluence page"

#5. Update parent page
print "Updating parent page"
data ={
	"id":args.id,
	"type":"page",
	"title":title,
	"space": {
		"key":space
	},
	"body": {
		"storage": {
			"value":storage,
			"representation":"storage"
			}
	},
	"version": {
		"number": version
	}
}

response = requests.put(putPageURL, data=dumps(data), headers=headers)
print response
assert str(response) == "<Response [200]>", "Failed to update parent Confluence page"
