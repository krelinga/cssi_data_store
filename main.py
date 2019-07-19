import os

from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def root_parent():
    '''A single key to be used as the ancestor for all dog entries.

    Allows for strong consistency at the cost of scalability.'''
    return ndb.Key('Parent', 'default_parent')

class Dog(ndb.Model):
    '''A database entry representing a single dog.'''
    name = ndb.StringProperty()
    kind = ndb.StringProperty()
    hungry = ndb.BooleanProperty()

class Cat(ndb.Model):
    name = ndb.StringProperty()
    favorite_food = ndb.StringProperty()
    sleepy = ndb.BooleanProperty()

class MainPage(webapp2.RequestHandler):
    '''The handler for displaying the main list of dogs, and for adding new dogs.'''
    def get(self):
        template = JINJA_ENVIRONMENT.get_template("templates/main.html")
        data = {
            'dogs': Dog.query(ancestor=root_parent()).fetch(),
            'cats': Cat.query(ancestor=root_parent()).fetch()
        }
        self.response.write(template.render(data))

    def post(self):
        new_dog = Dog(parent=root_parent())
        new_dog.name = self.request.get('dog_name')
        new_dog.kind = self.request.get('dog_kind')
        new_dog.hungry = bool(self.request.get('dog_hungry', default_value=''))
        new_dog.put()
        # redirect to '/' so that the get() version of this handler will run
        # and show the list of dogs.
        self.redirect('/')

class DeleteDogs(webapp2.RequestHandler):
    '''The handler for deleting dogs.'''
    def post(self):
        to_delete = self.request.get('to_delete', allow_multiple=True)
        for entry in to_delete:
            key = ndb.Key(urlsafe=entry)
            key.delete()
        # redirect to '/' so that the MainPage.get() handler will run and show
        # the list of dogs.
        self.redirect('/')

class NewCatsHandler(webapp2.RequestHandler):
    def post(self):
        new_cat = Cat(parent=root_parent())
        new_cat.name = self.request.get('cat_name')
        new_cat.favorite_food = self.request.get('cat_favorite_food')
        new_cat.sleepy = bool(self.request.get('cat_sleepy', default_value=''))
        new_cat.put()
        # redirect to '/' so that the get() version of this handler will run
        # and show the list of dogs.
        self.redirect('/')

class DeleteCats(webapp2.RequestHandler):
    '''The handler for deleting cats.'''
    def post(self):
        to_delete = self.request.get('to_delete', allow_multiple=True)
        for entry in to_delete:
            key = ndb.Key(urlsafe=entry)
            key.delete()
        # redirect to '/' so that the MainPage.get() handler will run and show
        # the list of dogs.
        self.redirect('/')

class FilterHandler(webapp2.RequestHandler):
    def get(self):
        selection = self.request.get("cat_selection")
        cats = []

        if selection == "all" or selection == "":
            cats = Cat.query(ancestor=root_parent()).fetch()
        elif selection == "sleepy":
            cats = Cat.query(Cat.sleepy == True)
        elif selection == "pizza":
            cats = Cat.query(Cat.favorite_food == "pizza")
        elif selection == "nopizza":
            cats = Cat.query(Cat.favorite_food != "pizza")
        else:
            cats = Cat.query(Cat.sleepy == False, ancestor=root_parent())

        template = JINJA_ENVIRONMENT.get_template("templates/filter.html")
        self.response.write(template.render({"cats": cats}))



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/new_cats', NewCatsHandler),
    ('/delete_dogs', DeleteDogs),
    ('/delete_cats', DeleteCats),
    ('/filter', FilterHandler)
], debug=True)
