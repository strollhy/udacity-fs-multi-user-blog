from model_datastore import Model
import random
import string
import hashlib


def make_salt():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

def make_pw(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    return hashlib.sha256(name + pw + salt).hexdigest(), salt

def valid_pw(name, pw, salt, h):
    return h == make_pw(name, pw, salt)[0]


class User(Model):
    @classmethod
    def signup(cls, data):
        ds = cls.get_client()

        query = ds.query(kind='User')
        query.add_filter('name', '=', data['name'])

        if list(query.fetch()):
            return

        entity = datastore.Entity(
            key=ds.key('User'),
            exclude_from_indexes=['password'])

        data['password'], data['salt'] = make_pw(data['name'], data['password'])
        entity.update(data)
        ds.put(entity)
        return cls.from_datastore(entity)

    @classmethod
    def login(cls, data):
        ds = cls.get_client()

        query = ds.query(kind='User')
        query.add_filter('name', '=', data['name'])
        users = list(query.fetch())

        if users and valid_pw(data['name'], data['password'], users[0]['salt'], users[0]['password']):
            return cls.from_datastore(users[0])
