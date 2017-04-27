import configparser

def config_parser():
	config = configparser.ConfigParser()

	config['Analytics'] = { 'couch_database' : 'http://localhost:5984/',
		'train_data' : 'db_train',
		'row_data' : 'sentiment',
		'afinn_dict' : 'AFINN-111.txt',
		'emojis_dict' : 'emojis.txt',
		'mining_dict_pos' : 'positive-words.txt',
		'mining_dict_neg' : 'negative-words.txt',
		'words_dict' : 'words_new.txt',
		'con_vec' : 'counter_model.pkl',
		'tfid_con_vec' : 'tfid_counter_model.pkl',
		'classifier' : 'lr_nectar.pkl',
		'classifier_tfid' : 'tfid_lr_nectar.pkl',
		'obj_features' : 'features',
		'obj_id' : '_id',
		'obj_is_read' : 'is_read',	# is_read determine if features is generated
		'obj_text' : 'text',
		'obj_label' : 'label',
		'obj_geo_code' : 'geo_code',
		'obj_has_processed' : 'has_processed'} # has_processed determine if preprocess has been done

	# Writing our configuration file to 'example.cfg'
	with open('config.ini', 'w' )as configfile:
		config.write(configfile)


def main():
	config_parser()


if __name__ == '__main__':
	main()