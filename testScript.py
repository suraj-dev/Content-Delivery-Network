import subprocess
import shlex
import urllib2

cmd='dig @cs5700cdnproject.ccs.neu.edu -p 40500 cs5700cdn.example.com'
# cmd='dig @ns1.netnames.net www.rac.co.uk CNAME'
proc=subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
out,err=proc.communicate()
#print out
index = out.find('ANSWER SECTION')
index2 = out.find('time')
#print out[index:index2].split()
IPaddr = out[index:index2].split()[6]
print IPaddr

response = urllib2.urlopen("http://" + IPaddr + ":40500/wiki/Goku", timeout = 5)
content = response.read()
print content


