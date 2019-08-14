import os

from zeep import xsd
from lxml import etree
from smev_int.singleton import Singleton
from .transport import Transport


XSD_PATH = 'xsd'


class Loader(metaclass=Singleton):
    def __init__(self, path=XSD_PATH):
        self._path = path
        self.schema = None
        self.load()

    def load(self):
        self.schema = xsd.Schema()
        for d in self.list_dirs(self._path):
            for f in self.list_files(d):
                tree = etree.parse(f)
                t = Transport(d)
                schema = xsd.Schema(tree.getroot(), transport=t)
                self.schema.merge(schema)

    @staticmethod
    def list_dirs(path):
        return [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    @staticmethod
    def list_files(path):
        return [os.path.join(path, d) for d in os.listdir(path) if os.path.isfile(os.path.join(path, d))]

    def get_element(self, name):
        template = '{{{}}}{}'
        for ns in self.schema.namespaces:
            fullname = template.format(ns, name)
            try:
                return self.schema.get_element(fullname)
            except:
                pass