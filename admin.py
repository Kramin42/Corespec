

import os
import subprocess
import logging
import tornado.web as web

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

dir_path = os.path.dirname(os.path.realpath(__file__))

# autorun init.sh
try:
    subprocess.call(['sh', os.path.join(dir_path, 'init.sh')])
except:
    logger.warning('Could not run init.sh!')

VERSION = 'flowmeter2-1.2.5b'

changelog_html = ''
with open(os.path.join(dir_path, 'changelog.html')) as f:
    changelog_html = f.read()

class AdminHandler(web.RequestHandler):
    def get(self):
        self.write("""
            <html><head>
                <title>Admin</title>
                <style>
                    h1 {{
                        font-size: 1.5em;
                    }}
                    h2 {{
                        font-size: 1.25em;
                    }}
                    h3 {{
                        font-size: 1em;
                    }}
                </style>
            </head>
            <body>
                <h1>Version {version}</h1>
                <form action="/admin" method="post">
                    <button type="submit" name="action" value="update">Update & Restart</button>
                </form>
                <div>
                    {changelog}
                </div>
            </body></html>
            """.format(
                version=VERSION,
                changelog=changelog_html
            )
        )

    def post(self):
        logger.debug(self.request.body)
        if self.get_body_argument("action")=="update":
            subprocess.call(['sh', os.path.join(dir_path, 'update.sh')])
        else:
            self.get()
