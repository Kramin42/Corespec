

import subprocess
import logging
import tornado.web as web

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

VERSION = '1.0'

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
            subprocess.call(['./update.sh'])
        else:
            self.get()