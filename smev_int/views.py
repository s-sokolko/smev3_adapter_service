import asyncio
import datetime
import logging
from sanic.response import json

from .models import Query, create_model_class
from .processors.query import QueryProcessor
from .core import app, auth

logger = logging.getLogger(__name__)


@app.route('/schedule_query/<query_type>/', methods=['POST'])
@auth.auth_required
async def schedule_query(request, query_type):
    query = Query(type=query_type, body=request.json)
    qp = QueryProcessor()
    request_id = await qp.send(query)
    return json({'request_id': request_id})


@app.listener('after_server_start')
async def get_reponse_periodic(app, loop):
    qp = QueryProcessor()
    while True:
        await asyncio.sleep(app.Config.RESPONSE_CHECK_TIMEOUT)
        try:
            await qp.get_response()
        except Exception as e:
            logger.exception(e)


@app.route('/get_document/<doctype>/<docid>')
@auth.auth_required
async def get_document(request, doctype, docid):
    cls = create_model_class(doctype)
    today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    params = {
        cls.identifier: docid,
        'created': {
            '$gte': today
        }
    }
    document = await cls.find_one(**params)
    status = 200 if document else 404
    return json(document, status=status)