import os
import re
import string
import random
import json
import time

import webapp2
import jinja2

import hashlib
import hmac

from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

                               
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

    
def email_key(name = 'default'):
    return db.Key.from_path('write club emails', name)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return email and EMAIL_RE.match(email)
    
def not_new_email(s):
    all_email = db.GqlQuery('select * from emailDB')
    val = False
    for e in all_email:
        if e.email == s:
            val = True
    return val
    
class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
class MainPage(BaseHandler):
    
    def get(self):
        self.render("clubmain.html")
        
    def post(self):
        email = self.request.get("email")
        
        if not_new_email(email):
            self.render("clubmain.html", eerror = "Oops! You're already on our mailing list.")
        elif valid_email(email):
            new_email = emailDB(parent = email_key(), email = email)
            new_email.put()
            self.redirect('/thankyou')
        else:
            self.render("clubmain.html", email = email, eerror = "ERROR: Invalid email")
        
        
class BoardPics(BaseHandler):

    def get(self):
        self.render("clubpics.html")
        
        
class ThankYou(BaseHandler):
    
    def get(self):
        self.render("thankyou.html")
        
class emailDB(db.Model):
    email = db.StringProperty(required = True)
            
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/eboard', BoardPics),
                               ('/thankyou', ThankYou)],
                              debug=True)
    