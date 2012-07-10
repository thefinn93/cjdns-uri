#! /usr/bin/env python
import sys
import ConfigParser
import subprocess
from urlparse import urlparse
from urlparse import parse_qs
import os
import shutil

parser=ConfigParser.SafeConfigParser()
try:
    parser.read([os.getenv("HOME") + '/.cjdnsadmin.ini'])
    import_path = parser.get('cjdns','importPath')
    adminPassword = parser.get('cjdns','adminpassword')
    adminPort = parser.getint('cjdns','adminport')
except:
    print """Config file not found or missing options.

Please make ~/.cjdnsadmin.ini and look a bit like this:
[cjdns]
importPath = <path to cjdns git>/contrib/python
adminpassword = <your admin password>
adminport = 11234"""
    sys.exit()

def addPeer(record):
    print "Adding peer..."
    sys.path.append(import_path)
    from cjdns import cjdns_connect
    cjdns = cjdns_connect("127.0.0.1", adminPort, adminPassword)
    cjdns.UDPInterface_beginConnection(record["key"],record["ip"] + ":" + record["port"],0,record["password"])

def confirm(record):
    print record
    if subprocess.call("zenity --question --text=\"Would you like to add this cjdns peer:\\nIP: " + record['ip'] + "\\nPort: " + str(record['port']) + "\\nPassword: " + record['password'] + "\nKey: " + record['key'] + "\"", shell=True) == 0:
        addPeer(record)

def registerGnome(path):
    # http://people.w3.org/~dom/archives/2005/09/integrating-a-new-uris-scheme-handler-to-gnome-and-firefox/
    # http://stackoverflow.com/questions/2051905/access-to-gnome-configuration-information-using-python
    out = True
    try:
        import gtk
        import gtk.glade
        import gconf
        client = gconf.client_get_default()
        client.set_string("/desktop/gnome/url-handlers/cjdns/command", str(path))
        client.set_bool("/desktop/gnome/url-handlers/cjdns/needs_terminal", False)
        client.set_bool("/desktop/gnome/url-handlers/tel/enabled", True)
    except:
        out = False
    return out

def registerXDG(path):
    try:
        desktop = open("/usr/share/applications/hyperboria.desktop","w")
        desktop.write("[Desktop Entry]\nType=Application\nTerminal=false\nExec=" + path + "\nName[en_US]=Hyperboria\nComment[en_US]=Open mesh network\nName=Hyperboria\nComment=Open Mesh Network\nIcon=/usr/share/icons/hicolor/scalable/apps/cjdns.svg\nMimeType=x-scheme-handler/cjdns;")
        desktop.close()
        subprocess.call("update-desktop-database", shell=True)
        return True
    except IOError:
        print "Oops! Try that again as root"
        return False
    except:
        return False

if len(sys.argv) == 1:
    print "Usage: " + sys.argv[0] + " install"
    print """Then click on a cjdns:// link and you'll
see a dialog asking if you'd like to add that peer.
Note that this only works in GNOME for the now, more
coming soon. If you can make it work in your DE, submit
pull request! This page seems to link to how tos for that:
http://wiki.gnucash.org/wiki/Custom_URI_Scheme"""
else:
    if sys.argv[1] == "install":
        try:
            shutil.copy(sys.argv[0],"/usr/bin/cjdns-uri")
        except:
            print "Failed to copy file. Try running this as root!"
            sys.exit()
        if registerGnome("python /usr/bin/cjdns-uri %s"):
            print "Registered GNOME protocol handler"
        else:
            print "Failed to register GNOME protocol handler"
        if registerXDG("python /usr/bin/cjdns-uri %U"):
            print "Registered XDG protocol handler"
        else:
            print "Failed to register XDG protocol handler"
    else:
        print sys.argv
        parsed = urlparse(" ".join(sys.argv[1:]).strip("'"))
        record = {"ip":":".join(parsed.netloc.split(":")[:-1]),"port":parsed.port}
        path = parse_qs(parsed.path)
        record['key'] = path['key'][0]
        record['password'] = path['password'][0]
        confirm(record)
