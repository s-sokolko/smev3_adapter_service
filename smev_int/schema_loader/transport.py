import zeep.transports
import os


from six.moves.urllib.parse import urlparse


class Transport(zeep.transports.Transport):
    def __init__(self, basedir, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self._basedir = basedir

    def load(self, url):
        """Load the content from the given URL"""
        if not url:
            raise ValueError("No url given to load")

        scheme = urlparse(url).scheme
        if scheme in ('http', 'https'):

            if self.cache:
                response = self.cache.get(url)
                if response:
                    return bytes(response)

            content = self._load_remote_data(url)

            if self.cache:
                self.cache.add(url, content)

            return content

        elif scheme == 'file':
            if url.startswith('file://'):
                url = url[7:]

        url = os.path.join(self._basedir, url)
        with open(os.path.expanduser(url), 'rb') as fh:
            return fh.read()