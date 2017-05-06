import sys
import configparser


def configcouchdb(ipaddress):
	config = configparser.ConfigParser()
	config['couchdb'] = {'uuid': '66f9f6c09234de0ba5c40fc630e44c49',
			     'database_dir': '/mnt/data',
			     'view_index_dir': '/mnt/data'}

	config['couch_peruser'] = {}

	config['chttpd'] = {'port' : '5984',
			    'bind_address': ipaddress,
			     'backlog': '512',
			     'docroot': './share/www',
			     'socket_options': '[{recbuf, 262144}, {sndbuf, 262144}, {nodelay, true}]'}

	config['httpd'] = { 'port': '5986',
			    'bind_address': ipaddress,
			    'authentication_handlers': '{couch_httpd_oauth, oauth_authentication_handler}, {couch_httpd_auth, cookie_authentication_handler}, 					                {couch_httpd_auth,default_authentication_handler}',
			    'default_handler': '{couch_httpd_db, handle_request}',
			    'secure_rewrites': 'true',
			    'vhost_global_handlers': '_utils, _uuids, _session, _oauth, _users',
			    'allow_jsonp':  'false'
			   }

	config['query_servers'] = { 'python': '/usr/bin/couchpy'}
	config['httpd_global_handlers'] = {}
	config['os_daemons'] = {}
	config['daemons'] = {}
	config['ssl'] = {}
	config['vhosts'] = {}
	config['update_notification'] = {}
	config['admins'] = {}


	with open('local.ini', 'w') as configfile:
		config.write(configfile)

	return


def main():
    
      ipaddress = sys.argv[1]
      configcouchdb(ipaddress)

if __name__ == "__main__":
    main()




