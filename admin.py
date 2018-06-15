

import os
import subprocess
import logging
import tornado.web as web

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

dir_path = os.path.dirname(os.path.realpath(__file__))

VERSION = '1.0.1'

class AdminHandler(web.RequestHandler):
    def get(self):
        self.write("""
            <html><head>
                <title>Admin</title>
            </head>
            <body>
                <h3>Version {version}</h3>
                <form action="/admin" method="post">
                    <button type="submit" name="action" value="update">Update & Restart</button>
                </form>
            </body></html>
            """.format(
                version=VERSION
            )
        )

    def post(self):
        logger.debug(self.request.body)
        if self.get_body_argument("action")=="update":
            subprocess.call(['sh', os.path.join(dir_path, 'update.sh')])
        else:
            self.get()
