import subprocess
import argparse
import sys


def stopHTTPServer():
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
		#ssh into the machine and kill the java process for the http server
		subprocess.call("ssh -i "+key+" "+username+"@"+server+ " 'killall java -u "+ username +"'", shell=True)

	print "HTTP Servers stopped"

def stopDNSServer():
	dnsServer = "cs5700cdnproject.ccs.neu.edu"
	#ssh into the machine and kill the python process for the dns server 
	subprocess.call("ssh -i "+key+" "+username+"@"+dnsServer+ " 'killall python -u "+ username +"'", shell=True)

	print "DNS server stopped"

#Ensure the command line arguments are correct
argParser = argparse.ArgumentParser(description='CDN stop')
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
stopHTTPServer()
stopDNSServer()
