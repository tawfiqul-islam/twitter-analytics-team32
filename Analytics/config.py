import configparser

def config_parser():
	config = configparser.ConfigParser()

	config['Analytics'] = { 'couch_database' : 'http://115.146.92.169:5986/',
		'couch_database_target' : 'http://115.146.92.169:5986/',
		'couch_ip_train' : 'http://115.146.92.169:5986/',
		'train_data' : 'train_data',
		'dict_dir' : './Dict',
		'row_data' : 'victoriastream',
		'target_data' : 'target_data',
		'food_dict' : 'food_dict.txt',
		'afinn_dict' : 'AFINN-111.txt',
		'emojis_dict' : 'emojis.txt',
		'mining_dict_pos' : 'positive-words.txt',
		'mining_dict_neg' : 'negative-words.txt',
		'words_dict' : 'words_new.txt',
		'con_vec' : 'counter_model.pkl',
		'tfid_con_vec' : 'tfid_counter_model.pkl',
		'classifier' : 'lr_nectar.pkl',
		'classifier_tfid' : 'tfid_lr_nectar.pkl',
		'classifier_mnb' : 'mnb_nectar.pkl',
		'classifier_neural' : 'neural_nectar.pkl',
		'obj_features' : 'features',
		'obj_id' : '_id',
		'obj_is_read' : 'is_read',	# is_read determine if features is generated
		'obj_text' : 'text',
		'obj_label' : 'label',
		'obj_geo_code' : 'geo_code',
		'obj_has_processed' : 'has_processed',
		'map_func_preprocess' : '''
			function(doc){
				if (!doc.has_processed){
					emit(doc._id, doc)
				}
			}
		''',
		'view_preprocess_vicstream' : '_design/victoriastream',
		'get_coordinates' : 'get_coordinates',
		'retrieved_field_vicstream' : 'victoriastream/get_coordinates',
		'host_dir' : 'ClusterManager/Ansible',
		'host_file' : 'hosts',
		'temp_' : 'temp_'
		} # has_processed determine if preprocess has been done

	#IP to identiy which VM we are, VM1 = db
	config['VMTag'] = {'VM1' : 'http://115.146.92.169:5986/',
	                   'VM2' : 'http://115.146.93.16:5986/',
	                   'VM3' : 'http://115.146.92.181:5986/',
	                   'VM4' : 'http://115.146.93.25:5986/',
	                   'VM1_DB' : 'harvest1',
	                   'VM2_DB' : 'harvest2',
	                   'VM3_DB' : 'harvest3',
	                   'VM4_DB' : 'harvest4'}

	# Writing our configuration file to 'example.cfg'
	with open('config.ini', 'w' )as configfile:
		config.write(configfile)


def main():
	config_parser()


if __name__ == '__main__':
	main()
