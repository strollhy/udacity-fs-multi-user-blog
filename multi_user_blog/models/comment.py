from model_datastore import Model, datastore
import datetime


class Comment(Model):
    @classmethod
    def upsert(cls, data, id=None):
        ds = cls.get_client()
        if id:
            key = ds.key('Comment', int(id))
            data['updated'] = datetime.datetime.utcnow()
        else:
            key = ds.key('Comment')
            data['created'] = datetime.datetime.utcnow()

        entity = datastore.Entity(
            key=key,
            exclude_from_indexes=['content'])

        entity.update(data)
        ds.put(entity)
        return cls.from_datastore(entity)

    @classmethod
    def index(cls, post_id):
        ds = cls.get_client()
        query = ds.query(kind='Comment')
        query.add_filter('post_id', '=', post_id)
        return list(map(cls.from_datastore, query.fetch()))

    @classmethod
    def read(cls, id):
        ds = cls.get_client()
        key = ds.key('Comment', int(id))
        comment = ds.get(key)
        return cls.from_datastore(comment)

    @classmethod
    def delete(cls, id):
        ds = cls.get_client()
        key = ds.key('Comment', int(id))
        ds.delete(key)
