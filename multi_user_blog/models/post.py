from model_datastore import Model, datastore
from comment import Comment
import datetime


class Post(Model):
    @classmethod
    def index(cls, limit=10, cursor=None, user_id=None):
        ds = cls.get_client()

        query = ds.query(kind='Post')

        if user_id:
            query.add_filter('user_id', '=', user_id)

        query_iterator = query.fetch(limit=limit, start_cursor=cursor)
        page = next(query_iterator.pages)

        entities = list(map(cls.from_datastore, page))
        next_cursor = (
            query_iterator.next_page_token.decode('utf-8')
            if query_iterator.next_page_token else None)

        return entities, next_cursor

    @classmethod
    def read(cls, id):
        ds = cls.get_client()
        key = ds.key('Post', int(id))
        post = ds.get(key)
        if post: post.comments = Comment.index(id)
        return cls.from_datastore(post)

    @classmethod
    def upsert(cls, data, id=None):
        ds = cls.get_client()
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
        return cls.from_datastore(entity)

    @classmethod
    def put(cls, entity):
        cls.get_client().put(entity)

    @classmethod
    def delete(cls, id):
        ds = cls.get_client()
        key = ds.key('Post', int(id))
        ds.delete(key)
