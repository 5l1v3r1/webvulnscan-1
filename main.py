import requests, sys
from bs4 import BeautifulSoup
from urlparse import parse_qsl
from crawler import Crawler

vulnerable = []

def getmethod(html):
	a = BeautifulSoup(html, "html.parser")
	for form in a.find_all("form"):
		get = form.get("method")
		if get:
			return get
			print get
		else:
			False
		
def getaction(html):
	a = BeautifulSoup(html, "html.parser")
	for form in a.find_all("form"):
		act = form.get("action")
		if act:
			return act
		else:
			False

def getinput(html, payload):
	global final
	simpan = []
	simpen_name = []
	simpen_value = []
	a = BeautifulSoup(html, "html.parser")
	for soup in a.find_all("input"):
		name = soup.get('name')
		type = soup.get('type')
		if type == None:
			pass
		else:
			if str(type) == "hidden":
				value = soup.get("value")
				namee = soup.get("name")
				simpen_name.append(namee)
				simpen_value.append(value)
			elif str(name) == "None":
				continue
			else:
				simpan.append(name)
	simpan3 = ""
	for i in simpan:
		simpan3 += i + "=" + payload + "&"
	kntl = ['%s=%s'%(asu, jancok) for asu, jancok in zip(simpen_name,simpen_value)]
	kkk = '&'.join(kntl)
	simpan3 += kkk
	return simpan3
	
def xss(url, method, param, payload):
	if method == "get" or method == "GET":
		if param.endswith("&"):
			param = param[:-1]
		result = requests.get(url, params=param).text
		if payload in result:
			if str("XSS_GET"+url) in vulnerable:
				pass
			else:
				vulnerable.append("XSS_GET"+url)
				print "[RISK] Cross Site Scripting"
				print "| Method : GET"
				print "| Payload : "+payload
				print "| Vulnerable Page : "+url
				print "| Query : "+param
				print "\n"
	if method == "post" or method == "POST":
		kntl = dict(parse_qsl(param))
		result = requests.post(url, data=kntl).text
		if payload in result:
			print "[RISK] Cross Site Scripting"
			print "| Method : POST"
			print "| Payload : "+payload
			print "| Vulnerable Page : "+url
			print "| Post Param : "+str(kntl)
			print "\n"

def exploit(url, html):
	method = getmethod(html)
	if getaction(html):
		action = getaction(html)
	else:
		action = "?"
	if "http://" in action or "https://" in action:
		submitto = action
	else:
		submitto = url + action
	if method == "get" or method == "GET":
		xss(submitto, method, getinput(html, '"><gh0st>'), '"><gh0st>')
	elif method == "post" or method == "POST":
		xss(submitto, method, getinput(html, '"><gh0st>'), '"><gh0st>')
	else:
		print("invalid method!!!")
		
def main(url):
	text = requests.get(url).text
	soup = BeautifulSoup(text, "html.parser")
	totalform = 0
	if soup.find_all("form"):
		for i in soup.find_all("form"):
			totalform = totalform + 1
			exploit(url, str(i))
			
abc = 0
class MyCrawler(Crawler):
	def process_document(self, doc):
		global abc
		if doc.status == 200:
			abc = abc + 1
			main(doc.url)
			sys.stdout.write("\r["+str(abc)+"] Crawling . . . !")
			sys.stdout.flush()
		else:
		    pass

try:
	target = sys.argv[1]
	if target.startswith("http://") or target.startswith("https://"):
		url = target
	else:
		url = "http://" + target
	if url.endswith("/"):
		url = url
	else:
		url = url + "/"
except:
	print("Run With : python2.7 main.py [url]")
	exit();
crawler = MyCrawler()
crawler.set_follow_mode(Crawler.F_SAME_HOST)
crawler.add_url_filter('\.(jpg|jpeg|gif|png|js|css|swf)$')
crawler.crawl(url)