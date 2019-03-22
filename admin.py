

import os
import re
import subprocess
import logging
import tornado.web as web

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

dir_path = os.path.dirname(os.path.realpath(__file__))

# autorun init.sh
try:
    subprocess.call(['sh', os.path.join(dir_path, 'init.sh')])
except:
    logger.warning('Could not run init.sh!')

VERSION = '1.1.10d'

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

                <form action="/admin" method="post">
                    Current WiFi Password:<br>
                    <input type="password" name="curr_wifi_pass"><br>
                    New WiFi Password:<br>
                    <input type="password" name="new_wifi_pass"><br>
                    Confirm New WiFi Password:<br>
                    <input type="password" name="new_wifi_pass_confirm"><br>
                    <button type="submit" name="action" value="change_wifi_pass">Change WiFi Password</button>
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
            self.write('Updating & Restarting system.')
            subprocess.call(['sh', os.path.join(dir_path, 'update.sh')])
        elif self.get_body_argument("action")=="change_wifi_pass":
            with open('/etc/create_ap.conf', mode='r') as f:
                wifi_ap_conf = f.read()
                curr_pass = re.search(r'PASSPHRASE=(.*)', wifi_ap_conf).group(1)
                logger.debug('current password: ' + curr_pass)
            if curr_pass == self.get_body_argument("curr_wifi_pass"):
                new_pass = self.get_body_argument("new_wifi_pass")
                if new_pass == self.get_body_argument("new_wifi_pass_confirm"):
                    wifi_ap_conf = wifi_ap_conf.replace('PASSPHRASE='+curr_pass, 'PASSPHRASE='+new_pass)
                    with open('/etc/create_ap.conf', mode='w') as f:
                        f.write(wifi_ap_conf)
                    self.write('Restarting system to use new wifi password.')
                    os.system('reboot now')
                else:
                    self.write('Error: "New Wifi Password" was different from "Confirm New WiFi Password"!')
            else:
                self.write('Error: "Current Wifi Password" was incorrect!')
        else:
            self.get()
