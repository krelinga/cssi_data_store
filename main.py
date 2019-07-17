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

class MainPage(webapp2.RequestHandler):
    '''The handler for displaying the main list of dogs, and for adding new dogs.'''
    def get(self):
        template = JINJA_ENVIRONMENT.get_template("templates/main.html")
        data = {
            'dogs': Dog.query(ancestor=root_parent()).fetch()
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


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/delete_dogs', DeleteDogs),
], debug=True)
