#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import urllib
from BeautifulSoup import BeautifulSoup
from google.appengine.ext.webapp import template

# bySeason

class MainHandler(webapp.RequestHandler):
    def get(self):
		self.response.out.write("""<a href="/tvshow">Select from list of known series</a>""")

class KnownSeriesSelector(webapp.RequestHandler):
    def get(self):
		self.response.out.write("""<a href="/tvshow/tt0364845">NCIS</a>""")

class TVShowHandler(webapp.RequestHandler):
	def get(self,tvid):
		f = urllib.urlopen("http://www.imdb.com/title/"+tvid+"/episodes")
		s = f.read()
		f.close()
		soup = BeautifulSoup(s)
		self.response.out.write("<h3>"+soup.html.head.title.string+"</h3>")
		options = soup('select', {'id' : 'bySeason'})[0].findAll('option')
		self.response.out.write(template.render('tvshowhandler.html', {'options':options}))

class SeasonHandler(webapp.RequestHandler):
    def get(self,tvid,season):
		f = urllib.urlopen("http://www.imdb.com/title/"+tvid+"/episodes?season="+season)
		s = f.read()
		f.close()
		soup = BeautifulSoup(s)
		even = soup('div', {'class' : 'list_item even'})
		odd = soup('div', {'class' : 'list_item odd'})
		episodes = []
		for i in range(1,len(odd)+len(even)):
			if(i % 2 == 0):
				e = even[i/2-1]
			else:
				e = odd[i/2]
			episode = e.div.a.div.div.string.strip()
			airdate = e.first('div', {'class' : 'airdate'}).string.strip()
			title = e.first('div', {'class' : 'info'}).strong.a.string.strip()
			desc = e.first('div', {'class' : 'item_description'}).string.strip()
			img = e.first('img', {'class' : 'zero-z-index' })['src'].strip()
			if(img[0] == "/"):
				img = "http://imdb.com"+img
			episodes.append({'image':img,'title':title,'episode':episode,'desc':desc,'airdate':airdate})
		self.response.out.write(template.render('seasonhandler.html', {'episodes':episodes}))
		

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
										  ('/tvshow/(.*)/season/(.*)',SeasonHandler),
										  ('/tvshow/(.*)',TVShowHandler),
										  ('/tvshow',KnownSeriesSelector)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
