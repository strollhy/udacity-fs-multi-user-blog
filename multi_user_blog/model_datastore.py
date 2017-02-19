# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import current_app
from google.cloud import datastore
import random
import string
import hashlib
import datetime


def init_app(app):
    pass


def get_client():
    return datastore.Client(current_app.config['PROJECT_ID'])


# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.
    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]
    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, list):
        entity = entity.pop()

    entity['id'] = entity.key.id
    return entity
# [END from_datastore]


# [START user]
def signup(data):
    ds = get_client()

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
    return from_datastore(entity)


def login(data):
    ds = get_client()

    query = ds.query(kind='User')
    query.add_filter('name', '=', data['name'])
    users = list(query.fetch())

    if users and valid_pw(data['name'], data['password'], users[0]['salt'], users[0]['password']):
        return from_datastore(users[0])


def make_salt():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))


def make_pw(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    return hashlib.sha256(name + pw + salt).hexdigest(), salt


def valid_pw(name, pw, salt, h):
    return h == make_pw(name, pw, salt)[0]
# [END user]


# [START post]
def index(limit=10, cursor=None, user_id=None):
    ds = get_client()

    query = ds.query(kind='Post')
    if user_id:
        query.add_filter('user_id', '=', user_id)

    query_iterator = query.fetch(limit=limit, start_cursor=cursor)
    page = next(query_iterator.pages)

    entities = list(map(from_datastore, page))
    next_cursor = (
        query_iterator.next_page_token.decode('utf-8')
        if query_iterator.next_page_token else None)

    return entities, next_cursor


def read(id):
    ds = get_client()
    key = ds.key('Post', int(id))
    post = ds.get(key)
    if post:
        post.user = ds.get(ds.key('User', int(post['user_id'])))
    return from_datastore(post)


def update(data, id=None):
    ds = get_client()
    if id:
        key = ds.key('Post', int(id))
        data['updated'] = datetime.datetime.utcnow()
    else:
        key = ds.key('Post')
        data['created'] = datetime.datetime.utcnow()

    entity = datastore.Entity(
        key=key,
        exclude_from_indexes=['content'])

    entity.update(data)
    ds.put(entity)
    return from_datastore(entity)


create = update


def delete(id):
    ds = get_client()
    key = ds.key('Post', int(id))
    ds.delete(key)
# [END post]