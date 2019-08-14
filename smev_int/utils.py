import datetime
from urllib.parse import urlparse
from zeep.xsd.valueobjects import CompoundValue
from decimal import Decimal


def get_db_from_connstr(connstr):
    return urlparse(connstr).path[1:]


def serialize_object(obj, target_cls=dict):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime.date):
        return datetime.datetime.combine(obj, datetime.datetime.min.time())

    if isinstance(obj, list):
        return [serialize_object(sub, target_cls) for sub in obj]

    if isinstance(obj, (dict, CompoundValue)):
        result = target_cls()
        for key in obj:
            result[key] = serialize_object(obj[key], target_cls)
        return result

    return obj