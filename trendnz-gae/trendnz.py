import cgi
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from harvester import Harvester
import logging
import os

class MainPage(webapp.RequestHandler):
    def get(self):
        articles = Harvester('feed1.txt').articles

        template_values = {
            'articles': articles,
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication(
                                         [('/', MainPage)],
                                         debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
