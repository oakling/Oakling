COUCH_SERVER_ROOT='localhost:5984'
COUCH_USERNAME='michael'
COUCH_PASSWORD=''

####### Couch Forms & Couch DB Kit Settings #######
def get_server_url(server_root, username, password):
    if username and password:
        return "http://%(user)s:%(pass)s@%(server)s" % {"user": username,
                                                        "pass": password,
                                                        "server": server_root }
    else:
        return "http://%(server)s" % {"server": server_root }

COUCH_SERVER = get_server_url(COUCH_SERVER_ROOT, COUCH_USERNAME, COUCH_PASSWORD)

