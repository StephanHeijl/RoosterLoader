import json,re,os,datetime
from mod_python import apache
from RoosterLoader import *

# Global faculty list
faculties = {	"FTK/IAS"	: "http://rooster.han.nl/SchoolplanFT_AS/",
				"FGGM"		: "http://rooster.han.nl/SchoolplanFGGM/rooster.asp"
			}

def index(req, faculty="FTK/IAS"):
	req.content_type = "text/html; charset=UTF-8"
	
	if faculty not in faculties:
		req.write("<script>window.location.href='index.py';</script>")
		return
	
	RL = RoosterLoader(url=faculties[faculty])
	
	fOptions = ""
	for f in faculties.keys():
		fOptions+="<option value='%s' %s>%s</option>\n" % (f,'selected="selected"' if faculty == f else "", f)
	
	options = ""
	for klas,id in sorted(RL.pd['options']['Klas'].items(), key=lambda k: k[0]):
		options+="<option value='%s'>%s</option>\n" % (id, klas)
	
	index = '/'.join(os.path.realpath(__file__).split("/")[:-1]) + "/index.htm"
	
	html = open(index).read().format( "<!--","-->",options,fOptions )
	
	req.write(html)

def results(req):
	req.content_type = "text/html"
	
	faculty = req.form['faculty'] or "FTK/IAS"
	if faculty not in faculties:
		req.write("<script>window.location.href='index.py';</script>")
		return
	
	RL = RoosterLoader(url=faculties[faculty])
	
	if 'download' in req.form and req.form['download'] == "yes":
		req.headers_out["Content-type"] = "application/force-download"
		req.headers_out["Content-Disposition"] = "attachment; filename=rooster.%s" % (req.form['format'][:3])
	
	# Check whether or not a cached version of the file exists
	cacheDir = '/'.join(__file__.split("/")[:-1] + ["cache"])
	cachedFiles = os.listdir(cacheDir)
	if "nz" in req.form['format']:
		cacheName = "%s_nz.cache.ics" % req.form['groep']
	else:
		cacheName = "%s.cache.ics" % req.form['groep']
	fromCached = False
	
	if cacheName in cachedFiles:
		# Check the modified date of the cache file
		cachedDate = datetime.date.fromtimestamp(int(os.path.getmtime(cacheDir + "/" + cacheName)))
		threeDaysAgo = (datetime.date.today() - datetime.timedelta(days=3))
		
		if  cachedDate > threeDaysAgo:
			cachedFile = open(cacheDir + "/" + cacheName, "r")
			rooster = cachedFile.read()
			cachedFile.close()
			fromCached = True
			
		else:
			rooster = RL.searchGroup(req.form['groep'],req.form['format'])
	else:
		rooster = RL.searchGroup(req.form['groep'],req.form['format'])
	
	if 'download' in req.form and req.form['download'] == "yes":		
		req.write( rooster )
	
	if req.form['format'] in ["ics","icsnz"] and not fromCached:
		try:
			cachedRooster = open(cacheDir + "/" + cacheName, "w")
		except Exception as e:
			req.write(str(e))
			return
			
		cachedRooster.write(rooster)
		cachedRooster.close()
		
def cache(req):
	# Check whether or not a cached version of the file exists
	req.headers_out["Content-type"] = "text/calendar; charset=utf-8"
	
	cacheDir = '/'.join(__file__.split("/")[:-1] + ["cache"])
	cachedFiles = os.listdir(cacheDir)
	if "nz" in req.form:
		cacheName = "%s_nz.cache.ics" % req.form['g']
	else:
		cacheName = "%s.cache.ics" % req.form['g']
	fromCached = False
	
	if cacheName in cachedFiles:
		# Check the modified date of the cache file
		cachedDate = datetime.date.fromtimestamp(int(os.path.getmtime(cacheDir + "/" + cacheName)))
		threeDaysAgo = (datetime.date.today() - datetime.timedelta(days=3))
	
		if cachedDate < threeDaysAgo:
			faculty = req.form['faculty'] or "FTK/IAS"
			if faculty not in faculties:
				req.write("<script>window.location.href='index.py';</script>")
				return
			
			RL = RoosterLoader(url=faculties[faculty])
			rooster = RL.searchGroup(req.form['g'], "icsnz" if "nz" in req.form.keys() else "ics")
			cachedRooster = open(cacheDir + "/" + cacheName, "w")
			cachedRooster.write(rooster)
			cachedRooster.close()
			
		else:
			cachedRooster = open(cacheDir + "/" + cacheName, "r")
			rooster = cachedRooster.read()
			cachedRooster.close()
		
		req.write( rooster )


