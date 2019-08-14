import asyncio
import uvloop
import signal
import logging

from sanic import Sanic
from sanic.response import text
from sanic_token_auth import SanicTokenAuth
import motor.motor_asyncio

from .adapter import Adapter
from .utils import get_db_from_connstr

from settings import Config

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__name__)


async def server_error_handler(request, exception):
    return text(str(exception), status=400)


async def init_resources(app, loop):
    url = Config.MONGO_URL
    client = motor.motor_asyncio.AsyncIOMotorClient(url, io_loop=loop)
    dbname = get_db_from_connstr(url)
    app.mongo = client[dbname]
    app.adapter = Adapter(**Config.ADAPTER_SETTINGS)
    app.asyncio_loop = loop


def handle_shutdown(sig, frame):
    logging.info('Received stop signal, cancelling tasks...')
    for task in asyncio.Task.all_tasks():
        task.cancel()
    logging.info('Bye, exiting in a minute...')


app = Sanic()
app.error_handler.add(Exception, server_error_handler)
app.register_listener(init_resources, 'before_server_start')
app.Config = Config
auth = SanicTokenAuth(app, secret_key=Config.API_KEY, header=Config.API_KEY_HEADER)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

