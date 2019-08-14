from smev_int.singleton import Singleton
from smev_int.schema_loader.loader import Loader
from smev_int.core import app
from smev_int.models import Query, create_model

from .exceptions import *


class QueryProcessor(metaclass=Singleton):
    def __init__(self):
        self.loader = Loader()

    async def send(self, query):
        element = self.loader.get_element(query.request_element)
        if not element:
            raise QueryNotSupported('Query type not supported')
        val = element(**query.body) if isinstance(query.body, dict) else element(*query.body)
        query.request_id = await app.asyncio_loop.run_in_executor(None, app.adapter.send, val)
        await query.save()
        return query.request_id

    async def _save_model_data(self, query, response_data):
        element = self.loader.get_element(query.response_element)
        parsed = element.parse(response_data, self.loader.schema)
        parsed['request_id'] = query.request_id
        instance = create_model(query.type, parsed)
        await instance.save()
        return instance

    async def get_response(self):
        response = await app.asyncio_loop.run_in_executor(None, app.adapter.get_response)
        if not response:
            return
        query = await Query.process_response(response)
        if not query:
            raise ReferencedMessageNotFound('Message not found for response {}'.format(str(response)))
        if not query.success:
            raise ErrorMessage(str(response))
        return await self._save_model_data(query, response['data'])