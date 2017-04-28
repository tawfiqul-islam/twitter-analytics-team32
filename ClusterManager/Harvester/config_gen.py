import configparser

config = configparser.ConfigParser()
config['HarvestConfig'] = { 'ConsumerKey' : 'qU0Pn8GfQwn2QCK0KZMt868R3',
                            'ConsumerSecret' : '8cayRMPWrL86l9aQr44bStUBrKDG8A9qcAjRdiUU2EQj9kA0Ou',
                            'AccessToken' : '92007701-fPTuS79V3mi9aBqSpYiHwhPnk6Fp6QzhJ6kGkeDS8',
                            'AccesTokenSecret' : '3a4BDmMz2IFylrQITZRzN3RNCDBK6lvwN89UZ0zGx3EBi',
                            'DatabaseIP' : 'http://115.146.95.73:5984/',
                            'DatabaseName' : 'victoriasearch',
                            'Location' : '140.888036,-39.05559,150.525361,-34.196400',
                            'SearchQuery' : '(Victoria, Australia) OR (Australia)'}

with open('config.ini', 'w') as configfile:
    config.write(configfile)
