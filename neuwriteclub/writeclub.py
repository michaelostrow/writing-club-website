import os
import re
import string
import random
import datetime

import webapp2
import jinja2

import hashlib
import hmac

from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
                               
month_dir = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
             7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November',
             12: 'December'}

                               
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

    
def club_key(name = 'default'):
    return db.Key.from_path('club site key', name)

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
    
def get_prompt():
    all_prompt = db.GqlQuery("select * from promptDB")
    all_prompt = list(all_prompt)
    if len(all_prompt) == 0:
        return "No prompts for you... yet!"
    else:
        return str(random.choice(all_prompt).text)
        
def get_archive():
    all_archive = db.GqlQuery("select * from archiveDB")
    all_archive = list(all_archive)
    
    
    
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
            new_email = emailDB(parent = club_key(), email = email)
            new_email.put()
            self.redirect('/thankyousu')
        else:
            self.render("clubmain.html", email = email, eerror = "ERROR: Invalid email")
        
class Prompts(BaseHandler):
    
    def get(self):
        the_prompt = get_prompt()
        self.render("prompts.html", the_prompt = the_prompt)
        
    def post(self):
        content = self.request.get("content")
        if content == '':
            the_prompt = get_prompt()
            self.render("prompts.html", the_prompt = the_prompt, perror = "Please type your prompt")
        else:
            new_prompt = promptDB(parent = club_key(), text = content)
            new_prompt.put()
            self.redirect('/thankyoupr')
            
            
class Archive(BaseHandler):

    def get(self):
        all_archive = db.GqlQuery('select * from archiveDB')
        all_archive = list(all_archive)
        self.render("archive.html", archive = all_archive)
        
class IndiArchive(BaseHandler):

    def get(self, archive_id):
        key = db.Key.from_path('archiveDB', int(archive_id), parent=club_key())
        to_render = db.get(key)
        self.render("indiarchive.html", archive = to_render)
        
class ArchiveSubmit(BaseHandler):

    def get(self):
        self.render("archivesubmit.html")
        
    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        if (title == '') or (content == ''):
            self.render("archivesubmit.html", tval = title, cval = content, eerror = "Incomplete entry")
        else:
            new_archive = archiveDB(parent = club_key(), title = title, text = content)
            new_archive.put()
            self.redirect("/archive")
        
    
class BoardPics(BaseHandler):

    def get(self):
        self.render("picscontent.html")
        
        
class ThankYouSU(BaseHandler):
    
    def get(self):
        self.render("thankyousu.html")
        
class ThankYouP(BaseHandler):
    
    def get(self):
        self.render("thankyoupr.html")
        
class emailDB(db.Model):
    email = db.StringProperty(required = True)
    
class promptDB(db.Model):
    text = db.TextProperty(required = True)
    
class archiveDB(db.Model):
    title = db.StringProperty(required = True)
    text = db.TextProperty(required = True)
    submit_date = db.DateProperty(required = True, auto_now_add = True)
    
            
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/eboard', BoardPics),
                               ('/thankyousu', ThankYouSU),
                               ('/thankyoupr', ThankYouP),
                               ('/prompts', Prompts),
                               ('/archive', Archive),
                               ('/archive/([0-9]+)', IndiArchive),
                               ('/archivesubmit', ArchiveSubmit)],
                              debug=True)
    