import subprocess
import argparse
import sys


def deployHTTPServer():

	#replica servers
	servers = ['ec2-54-210-1-206.compute-1.amazonaws.com',
				'ec2-54-67-25-76.us-west-1.compute.amazonaws.com',
				'ec2-35-161-203-105.us-west-2.compute.amazonaws.com',
				'ec2-52-213-13-179.eu-west-1.compute.amazonaws.com',
				'ec2-52-196-161-198.ap-northeast-1.compute.amazonaws.com',
				'ec2-54-255-148-115.ap-southeast-1.compute.amazonaws.com',
				'ec2-13-54-30-86.ap-southeast-2.compute.amazonaws.com',
				'ec2-52-67-177-90.sa-east-1.compute.amazonaws.com',
				'ec2-35-156-54-135.eu-central-1.compute.amazonaws.com']
	

	for server in servers:
		#transfer the files
		subprocess.call("scp -i"+key+" deployCDN deployCDN.py runCDN runCDN.py stopCDN stopCDN.py dnsserver dnsserver.py httpserver httpserver.jar makefile "+username+"@"+server+":~", shell=True)
		subprocess.call("ssh -i "+key+" "+username+"@"+server+" 'mkdir HTMLFiles mapper'", shell=True)

		#run the make command
		subprocess.call("ssh -i "+key+" "+username+"@"+server+" 'make'", shell=True)
		
		

	print "HTTP Servers deployed"

def deployDNSServer():
	dnsServer = "cs5700cdnproject.ccs.neu.edu"
	subprocess.call("scp -i"+key+" deployCDN deployCDN.py runCDN runCDN.py stopCDN stopCDN.py httpserver httpserver.jar makefile dnsserver dnsserver.py "+username+"@"+dnsServer+":~", shell=True)
	subprocess.call("ssh -i "+key+" "+username+"@"+dnsServer+" 'make'", shell=True)
	print "DNS server deployed"

#Parse all the command line arguments
argParser = argparse.ArgumentParser(description='CDN deploy')
argParser.add_argument('-p', dest='portNumber', help='please input an integer between 40000-60000', type=int)
argParser.add_argument('-o', dest='originServer', help='please input the origin server')
argParser.add_argument('-n', dest='nameServer', help='please input the name server')
argParser.add_argument('-i', dest='privateKey', help='please input the private keyfile')
argParser.add_argument('-u', dest='userName', help='please enter the username for the user logged in')

arguments = argParser.parse_args()

if arguments.portNumber is None:
	print 'portNumber not specified'
	sys.exit()

if arguments.originServer is None:
	print 'origin server not specified'
	sys.exit()

if arguments.nameServer is None:
	print 'name server not specified'
	sys.exit()

if arguments.privateKey is None:
	print 'private key not specified'
	sys.exit()

if arguments.userName is None:
	print 'user name not specified'
	sys.exit()

portNo = arguments.portNumber
origin = arguments.originServer
name = arguments.nameServer
key = arguments.privateKey
username = arguments.userName
deployHTTPServer()
deployDNSServer()