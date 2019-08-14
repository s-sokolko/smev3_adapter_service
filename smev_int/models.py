import datetime
from bson import ObjectId

from .core import app
from .utils import serialize_object


class Model(dict):
    """
    A simple async model that wraps mongodb document using motor
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    @property
    def fields(self):
        return {k: v for k, v in self.items() if k != '_id'}

    @property
    def collection(self):
        classname = type(self).__name__
        return app.mongo[classname]

    async def save(self):
        if not self._id:
            self.created = datetime.datetime.now()
            return await self.collection.insert_one(self)
        else:
            return await self.collection.replace_one({"_id": ObjectId(self._id)}, self.fields)

    async def reload(self):
        if self._id:
            self.update(await self.collection.find_one({"_id": ObjectId(self._id)}))

    async def remove(self):
        if not self._id:
            return
        await self.collection.delete_one({"_id": ObjectId(self._id)})
        self.clear()

    @classmethod
    async def find_one(cls, **kwargs):
        collection = app.mongo[cls.__name__]
        data = await collection.find_one(kwargs)
        if not data:
            return None
        data['_id'] = str(data['_id'])
        return cls(data)


class Query(Model):
    @property
    def request_element(self):
        return '{}Request'.format(self.type)

    @property
    def response_element(self):
        return '{}Response'.format(self.type)

    @classmethod
    async def process_response(cls, response):
        msg_id = response['reference_id']
        query = await cls.find_one(request_id=msg_id)
        if not query:
            return
        # update referenced query status
        query.success = response['success']
        query.response_received = datetime.datetime.now()
        await query.save()
        return query


class _Document(Model):
    """
    Do not create objects of this class.
    Use factory functions instead
    """
    async def save(self):
        await self.remove_duplicates()
        await super().save()

    async def remove_duplicates(self):
        await self.collection.delete_many({self.identifier: self.get(self.identifier)})


def create_model_class(name):
    cls = type(name,
               (_Document, ),
               {'identifier': app.Config.DOCUMENT_IDENTIFIERS.get(name)})
    return cls


def create_model(name, mapping=None, **kwargs):
    cls = create_model_class(name)
    mapping = serialize_object(mapping)
    kwargs = {key: serialize_object(kwargs[key]) for key in kwargs.keys()}
    return cls(mapping, **kwargs)
