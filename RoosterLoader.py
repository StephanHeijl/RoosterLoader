# laad roosterdata
import requests
from HTMLParser import HTMLParser
from pprint import pformat as pf
import datetime, time, uuid

class RoosterParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		
		self.pagedata = {"options":{"Week":[], "Klas":[], "Lokaal":[], "Leraar":[]}}
		self.isOption = False
		self.loadData = False
		self.startLoading = False
		self.now = datetime.datetime.now()
		self.day = 0
		self.hour = ""
		
	def handle_starttag(self, tag, attrs):
		attributes = dict(attrs)
		if tag == "option":
			value = str(attributes['value'])
			self.isOption = value
		if tag == "table" and attributes['class'] == "data":
			self.startLoading = True
			self.rooster = {}
			self.datums = []
		if tag == "td" and self.startLoading:
			self.day+=1
							
	def handle_data(self,data):
		if self.isOption and not self.loadData:
			value = self.isOption
			d = data.encode('utf-8')
			if all([c not in d for c in ["\t","\r","\n", ":", "t/m", "Toon"]]):
				if "/" in value:
					self.pagedata['options']['Week'].append([d,value])
				elif "(" in d or "Lok" in d or "_" in d:
					self.pagedata['options']['Lokaal'].append([d,int(value)])
				elif d.upper() == d and "-" not in d:
					self.pagedata['options']['Leraar'].append([d,int(value)])
				else:
					self.pagedata['options']['Klas'].append([d,int(value)])
			value = False
		
		elif self.loadData and self.startLoading:
			if len(data) in [3,4,5]:				
				if "-" in data and " " not in data:
					self.datums.append(str(data))
				if ":" in data:
					self.hour = data
					self.day = 0
				
			else:
				if len(data) > 3 and len(self.datums) > 0:
					#print data, self.day
					datum = self.datums[self.day-1]
					
					if abs( int(datum.split("-")[1]) - self.now.month ) > 3:
							year = self.now.year-1 
					else:
						year = self.now.year
						
					self.rooster[ time.strptime( str(" ".join([str(year), datum, self.hour])), "%Y %d-%m %H:%M" ) ] = data
			
	def getPageData(self):
		pagedata = self.pagedata
		for on in pagedata['options'].keys():
			pagedata['options'][on] = dict(self.pagedata['options'][on])
		return pagedata

class RoosterLoader():
	def __init__(self, url=None):
		self.url = url or "http://rooster.han.nl/SchoolplanFT_AS/rooster.asp"
		r = requests.post(self.url)
		self.parser = RoosterParser()
		page = r.text.replace('""','"')
		body = page[page.index("<body>")+6:page.index("</body>")].strip("\n")
		self.parser.feed(body)		
				
		self.pd = self.parser.getPageData()
		
	def searchGroup(self,gr,format):
		groep = gr
		planning = []
		
		
		# Loop through all the weeks 
		w = self.parser.now.isocalendar()[1]
		for wn, week in self.pd['options']['Week'].items():
			if (abs(w - int(wn)) > 12 or w > int(wn)) and wn not in range(40,52):
				continue
			
			planning += self.requestRooster(groep,week)
		
		if format == "csv":
			return self.makeCSV(planning)
		if format == "ics":
			return self.makeiCal(planning)
		if format == "icsnz":
			filteredPlanning = filter(lambda e: "zelfst" not in e[1].lower() , planning)
				
			return self.makeiCal(filteredPlanning)
	
	def makeCSV(self, planning):
		csv = "Subject,Start Date,Start Time,End Date,End Time,All Day\n"
		for event in planning:
			# Turns out, datetime and time do NOT like each other
			t = datetime.datetime.fromtimestamp(time.mktime(event[0]))
			csv += ','.join([ event[1],
							 time.strftime("%d/%m/%Y",t.timetuple() ),
							 time.strftime("%H:%M", t.timetuple()),
							 time.strftime("%d/%m/%Y", (t + datetime.timedelta(minutes=45)).timetuple() ),
							 time.strftime("%H:%M", (t + datetime.timedelta(minutes=45)).timetuple() ),
							 "false"
							 ]) + "\n"
		return csv
		
	def makeiCal(self, planning):
		ical = ["""BEGIN:VCALENDAR
			VERSION:2.0
			PRODID:Stephan Heijl's RoosterLoader
			BEGIN:VTIMEZONE
			TZID:Europe/Amsterdam
			BEGIN:DAYLIGHT
			TZOFFSETFROM:+0100
			TZOFFSETTO:+0200
			DTSTART:19810329T020000
			RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
			TZNAME:CEST
			END:DAYLIGHT
			BEGIN:STANDARD
			TZOFFSETFROM:+0200
			TZOFFSETTO:+0100
			DTSTART:19961027T030000
			RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
			TZNAME:CET
			END:STANDARD
			END:VTIMEZONE""".replace("\t","").replace("\n","\r\n")]
		
		for event in planning:
			ical.append( "BEGIN:VEVENT" )
			ical.append( "UID:" + uuid.uuid4().hex )
			t = datetime.datetime.fromtimestamp(time.mktime(event[0]))
			ical.append( "SUMMARY:"+ event[1] )
			ical.append( "DTSTART:" + time.strftime("%Y%m%dT%H%M00",t.timetuple() ) )
			ical.append( "DTEND:" + time.strftime("%Y%m%dT%H%M00", (t + datetime.timedelta(minutes=45)).timetuple() ) )
			ical.append("END:VEVENT")
		
		ical.append("END:VCALENDAR")
		return '\r\n'.join(ical)
		
		
	def requestRooster(self, groep, week):
		parameters = { 
			"afdeling" : "0",
			"groep" : groep,
			"docent" : "0",
			"lokaal" : "0",
			"StartWeek" : week.strip(" \n"),
			"lestijden" : "on",
			"wijzigingen" : "on"
		}
		headers = {
			'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.45 Safari/537.17",
			'Content-Type' : "application/x-www-form-urlencoded"
		}
		r = requests.post(self.url, data=parameters, headers=headers )		

		page = r.text.replace('""','"')
		body = page[page.index("<body>")+6:page.index("</body>")].strip("\n")
		
		parser = RoosterParser()
		
		parser.loadData = True
		parser.feed(body)
		
		return parser.rooster.items()
