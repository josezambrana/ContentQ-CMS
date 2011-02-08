from users.models import InvalidPassword
from users.models import User
from users.models import UserDoesNotExist

class ModelBackend(object):
  def authenticate(self, username=None, password=None):
    return User.authenticate(username=username, password=password)