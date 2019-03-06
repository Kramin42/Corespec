import logging
import tornado.web as web


class FlowmeterHandler(web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path:
            url_path = 'flowmeter.html'
        return url_path
