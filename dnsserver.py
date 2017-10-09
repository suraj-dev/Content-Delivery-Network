import socket
import sys
import struct
import re
import urllib2
import json
import operator
from math import sin, cos, sqrt, atan2, radians

portNumber = ''
cdnName = ''

#replica servers
httpServers = ['54.210.1.206', '54.67.25.76', '35.161.203.105', '52.213.13.179', '52.196.161.198', '54.255.148.115', '13.54.30.86', '52.67.177.90', '35.156.54.135']

#store client IP address to resolve queries faster
clientCache = {}

#Storing latitude and longitude values for the HTTP servers
ipGeoLoc = {
	'54.210.1.206': [39.0481, -77.4729],
	'54.67.25.76': [37.3388, -121.8914],
	'35.161.203.105': [45.8696, -119.688],
	'52.213.13.179': [53.3331, -6.2489],
	'52.196.161.198': [35.6850, 139.7514],
	'54.255.148.115': [1.2931, 103.8558],
	'13.54.30.86': [-33.8612, 151.1982],
	'52.67.177.90': [-23.4733, -46.6658],
	'35.156.54.135': [50.1167, 8.6833]
}

#Ensure command line arguments are correct
if(len(sys.argv) == 5 and sys.argv[1] == '-p' and sys.argv[3] == '-n'):
	portNumber = int(sys.argv[2])
	cdnName = sys.argv[4]

else:
	print "Invalid parameters entered"
	sys.exit()

#Create a UDP socket
def createSocket(hostIp, portNo):
	try:
		sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sc.bind((hostIp, portNo))
		return sc

	except socket.error , msg:
		print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()

#Get IP address of the local machine
def getSourceIpAddress():
    sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sc.connect(('www.google.com', 80))
    source_ip = sc.getsockname()[0]
    sc.close()
    return source_ip

#get the best IP address to return based on closest replica
def getBestIpAddress(clientIp):
	response = urllib2.urlopen('http://freegeoip.net/json/' + str(clientIp))
	data = json.loads(response.read())
	#print data
	latitude = float(data['latitude'])
	longitude = float(data['longitude'])
	distances = calculateGeoLocationDistance(latitude, longitude)
	sortedDistances = sorted(distances.items(), key=operator.itemgetter(1))
	return sortedDistances[0][0]

#calculate distances from replica servers to client machine
def calculateGeoLocationDistance(latitude, longitude):
	lat1 = radians(latitude)
	lon1 = radians(longitude)
	distances = {}
	for ip, values in ipGeoLoc.iteritems():
		lat2 = radians(values[0])
		lon2 = radians(values[1])

		dlon = lon2 - lon1
		dlat = lat2 - lat1

		a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))

		distance = 6373 * c
		distances[ip] = distance
	return distances


#extract domain name from the query
def getDomainName(data):
	dataLength = struct.unpack('!B', data[0])[0]
	i=1
	domainName = ''
	while(dataLength != 0):
		j= i + dataLength
		if domainName:
			domainName = domainName + '.' + struct.unpack(str(dataLength) + 's',data[i:j])[0]
		else:
			domainName = struct.unpack(str(dataLength) + 's',data[i:j])[0]
		i = j + 1
		dataLength = struct.unpack('!B',data[j])[0]
	questionType = struct.unpack('!H',data[j+1:j+3])[0]
	questionClass = struct.unpack('!H',data[j+3:j+5])[0]
	return domainName, questionType, questionClass

#construct the response for the DNS Query
def constructResponse(data):
	#print str(data[12:])
	clientAddress = data[1]
	clientIPAddress = data[1][0]
	#print "clientAddress = " + str(clientAddress)
	request = data[0]
	queryHeaders = struct.unpack('!HHHHHH',request[0:12])
	#TransactionID = queryHeaders[0]
	#flags = queryHeaders[1]
	noOfQues = queryHeaders[2]
	noOfQuesAnswered = 1
	
	domainName, questionType, questionClass = getDomainName(request[12:])
	#print str(domainName)
	#print 'domain name extracted : ' + str(domainName)
	if cdnName != domainName:
		print 'The requested domain server name did not match'
		sys.exit()
	#flags = data[2:4]
	query = request[12:]
	responseHeader = request[0:2] + '\x81\x80' + struct.pack('!HHHH', noOfQues, noOfQuesAnswered, 0, 0)
	#ipAddress = '54.210.1.206'
	ipAddressToReturn = ''
	if str(clientIPAddress) in clientCache:
		ipAddressToReturn = clientCache[str(clientIPAddress)]
	else:
		ipAddressToReturn = getBestIpAddress(clientIPAddress)
		clientCache[str(clientIPAddress)] = ipAddressToReturn
	#ipLen = len(ipAddressToReturn)
	ipSplit = ipAddressToReturn.split('.')
	packStr = '!HHLHBBBB'
	answer = struct.pack(packStr, questionType, questionClass, 4, 4, int(ipSplit[0]), int(ipSplit[1]), int(ipSplit[2]), int(ipSplit[3]))
	response = responseHeader + query + '\xc0\x0c' + answer
	return response, clientAddress

sourceIP = getSourceIpAddress()
sock = createSocket(sourceIP, portNumber)

#Keep listening for incoming requests until the process is killed
while True:
	#print 'Server listening at port = ' + str(portNumber)
	#print 'myIP addr = ' + sourceIP
	request = sock.recvfrom(1024)
	#print "DNS request received"
	length = len(request[0])
	#print str(length)
	response, clientIP = constructResponse(request)
	sock.sendto(response, clientIP)
sock.close()

