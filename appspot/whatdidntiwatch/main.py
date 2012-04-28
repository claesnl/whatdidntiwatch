#!/usr/bin/env python
from google.appengine.api import users
import datetime
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import urllib
import cgi
from BeautifulSoup import BeautifulSoup
from google.appengine.ext.webapp import template

class Subscriptions(db.Model):
    account = db.UserProperty()
    tvid = db.StringProperty(required=True)
    last_seen_season = db.IntegerProperty(required=True)
    last_seen_episode = db.IntegerProperty(required=True)

class NewSeason(webapp.RequestHandler):
    def post(self):
        series = cgi.escape(self.request.get('series'))
        f = urllib.urlopen("http://www.imdbapi.com/?i=&t="+series)
        q = f.read()
        qq = q.split(':')
        qqq = qq[1].split(",")
        self.response.out.write(qqq[0])
        s = Subscriptions(account=users.get_current_user(),
                          tvid="123",
                          last_seen_season=1,
                          last_seen_episode=0)
        #s.put()

class MainHandler(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            subscriptions = Subscriptions.all()
            subscriptions.filter("account =", user)
            options = {
               'nickname'  : user.nickname() ,
               'logouturl' : users.create_logout_url("/") ,
               'series'    : subscriptions
            }
            self.response.out.write(template.render('welcome.html', options))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." % users.create_login_url("/"))
            self.response.out.write("<html><body>%s</body></html>" % greeting)

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
										  ('/tvshow',KnownSeriesSelector),
										  ('/newseason',NewSeason)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
