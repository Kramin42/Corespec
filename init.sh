#! /bin/sh
#TODO: autorun this script on startup

# set random mac address if none is set
prefix="02:"
suffix=$(openssl rand -hex 5 | sed 's/\(..\)/\1:/g; s/.$//')
macaddr=$prefix$suffix
echo $macaddr
sed -i "s/NEW_MACADDR=\w*\$/NEW_MACADDR=${macaddr}/" /etc/create_ap.conf
