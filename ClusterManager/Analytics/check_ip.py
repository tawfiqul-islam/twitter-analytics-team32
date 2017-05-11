import couchdb

def check_which_db(ip1, ip2, ip3, ip4, db1,	db2, db3, db4, my_ip):
	my_ip = 'http://' + my_ip + ":5986/"
	couch = ""
	db = ""
	if my_ip == ip1:
		couch = couchdb.Server(ip1)
		db = couch[db1]
	elif my_ip == ip2:
		couch = couchdb.Server(ip2)
		db = couch[db2]
	elif my_ip == ip3:
		couch = couchdb.Server(ip3)
		db = couch[db3]
	elif my_ip == ip4:
		couch = couchdb.Server(ip4)
		db = couch[db4]
	else:
		print("The ip address is wrong")

	return couch, db

def get_all_db(ip0, ip1, ip2, ip3, db0,	db1, db2, db3):
	db_list = []
	IP = 'ip'
	for i in range(4):
		couch = couchdb.Server(IP+str(i))
		db = couch[db+str(i)]
		db_list.append(db)
	return db_list
