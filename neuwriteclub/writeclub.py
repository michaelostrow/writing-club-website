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

secret = '32017a2f02f822db7bfcbd5f5783c6d0b69faae2775e138cffee5b0d9091cf41'

                               
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
        
def get_blog_posts():
    all_blog = db.GqlQuery("select * from blogDB limit 10")
    all_blog = list(all_blog)
    return all_blog
    
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
            
            
class Archive(BaseHandler):

    def get(self):
        self.render("archive.html")

            
class EventsHandler(BaseHandler):

    def get(self):
        f = open('events.txt')
        l = []
        while True:
            line = f.readline()
            l.append(line)
            if not line: break
        self.render("events.html", events = l)

class BlogHandler(BaseHandler):

    def get(self):
        blog_posts = get_blog_posts()
        self.render("blog.html", blog_posts = blog_posts)


class SubmitHandler(BaseHandler):

    def get(self):
        self.render("blogsubmit.html")  

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        password = self.request.get("password")
        if (title == '') or (content == ''):
            self.render("blogsubmit.html", titlev = title, textv = content,
                        passv = "", eerror = "Incomplete Entry")
        elif (hashlib.sha256(password).hexdigest() != secret):
             self.render("blogsubmit.html", titlev = title, textv = content,
                        passv = "", eerror = "Incorrect Password")
        else:
            new_archive = blogDB(parent = club_key(), title = title, text = content)
            new_archive.put()
            self.redirect("/blog")  
    
class BoardPics(BaseHandler):

    def get(self):
        self.render("clubpics.html")
        
        
class ThankYouSU(BaseHandler):
    
    def get(self):
        self.render("thankyousu.html")

        
class ThankYouP(BaseHandler):
    
    def get(self):
        self.render("thankyoupr.html")

        
class emailDB(db.Model):
    email = db.StringProperty(required = True)


class blogDB(db.Model):
    title = db.StringProperty(required = True)
    text = db.StringProperty(required = True)
    submit_date = db.DateProperty(required = True, auto_now_add = True)    
    
            
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/eboard', BoardPics),
                               ('/thankyousu', ThankYouSU),
                               ('/thankyoupr', ThankYouP),
                               ('/archive', Archive),
                               ('/events', EventsHandler),
                               ('/blog', BlogHandler),
                               ('/blogsubmit', SubmitHandler)],
                              debug=True)
    