These file are mainly to use generate dataset, make classifier and label the data


============================================
main files:
1. main_train_neg.py
2. main_neg.py
3. main_classifier.py

============================================
*command to run:
1. generate training data:
		python3 main_train_neg.py config.ini
2. predict row data, label it and store in db
		python3 main_neg.py config.ini
3. generate classifier
	python3 main_classifier.py config.ini
** we recommend that if runing classification, it is better to open up cloud_ipython.ipynb and run it on the machine which has more than 8 gb memory