import os,sys
from django.core.handlers.wsgi import WSGIHandler
 
if not os.path.dirname(__file__) in sys.path[:1]:
    sys.path.insert(0, os.path.dirname(__file__))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings_prod'
application = WSGIHandler()