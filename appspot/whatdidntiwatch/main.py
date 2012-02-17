#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import urllib
from BeautifulSoup import BeautifulSoup

# bySeason

class MainHandler(webapp.RequestHandler):
    def get(self):
		self.response.out.write("""<a href="/tvshow">Select from list of known series</a>""")

class KnownSeriesSelector(webapp.RequestHandler):
    def get(self):
		self.response.out.write("""<a href="/tvshow/tt0364845">NCIS</a>""")

class TVShowHandler(webapp.RequestHandler):
	def get(self,tvid):
		# bySeason
		f = urllib.urlopen("http://www.imdb.com/title/"+tvid+"/episodes")
		s = f.read()
		f.close()
		soup = BeautifulSoup(s)
		self.response.out.write("<h3>"+soup.html.head.title.string+"</h3>")
		options = soup('select', {'id' : 'bySeason'})[0].findAll('option')
		for w in options:
			self.response.out.write("<a href=\"/tvshow/tt0364845/season/"+w.string.lstrip()+"\">NCIS SEASON "+w.string.lstrip()+"</a><br />")

class SeasonHandler(webapp.RequestHandler):
    def get(self,tvid,season):
		self.response.out.write("<h1>NCIS</h1>")
		f = urllib.urlopen("http://www.imdb.com/title/"+tvid+"/episodes?season="+season)
		s = f.read()
		f.close()
		soup = BeautifulSoup(s)
		even = soup('div', {'class' : 'list_item even'})
		odd = soup('div', {'class' : 'list_item odd'})
		
		for i in range(1,len(odd)+len(even)):
			if(i % 2 == 0):
				e = even[i/2-1]
			else:
				e = odd[i/2]
			episode = e.div.a.div.div.string
			airdate = e.first('div', {'class' : 'airdate'}).string
			title = e.first('div', {'class' : 'info'}).strong.a.string
			desc = e.first('div', {'class' : 'item_description'}).string
			img = e.first('img', {'class' : 'zero-z-index' })['src']
			if(img[0] == "/"):
				img = "http://imdb.com"+img
			self.response.out.write("<h3><img src=\""+img+"\" />"+episode+"</h3>")
			self.response.out.write("<br />")
			self.response.out.write("AIRDATE: <b>"+airdate+"</b>")
			self.response.out.write("<br />")
			self.response.out.write("TITLE: <b>"+title+"</b>")
			self.response.out.write("<br />")
			self.response.out.write("DESCRIPTION: <b>"+desc+"</b>")
			self.response.out.write("<br />")
		

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
										  ('/tvshow/(.*)/season/(.*)',SeasonHandler),
										  ('/tvshow/(.*)',TVShowHandler),
										  ('/tvshow',KnownSeriesSelector)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
