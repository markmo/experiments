# Create your views here.

from django.http import Http404,HttpResponseRedirect
from django.shortcuts import render_to_response
from couchdb import Server
from couchdb.client import ResourceNotFound

server = Server('http://127.0.0.1:5984')
db = server['trendnz']

def index(request):
    words = db.get('_view/words')
    