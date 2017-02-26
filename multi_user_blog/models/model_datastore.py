# Main model class using Google Cloud datastore

from flask import current_app
from google.cloud import datastore


class Model(object):
    @classmethod
    def get_client(cls):
        if not hasattr(cls, 'client'):
            cls.client = datastore.Client(current_app.config['PROJECT_ID'])
        return cls.client

    @classmethod
    def from_datastore(cls, entity):
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
