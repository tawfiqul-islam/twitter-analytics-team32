from couchdb.mapping import Document, TextField, IntegerField, DateTimeField, BooleanField
class TrainData(Document):
	t_id = IntegerField()
	text = TextField()
	label = IntegerField()
	features = TextField()
	geo_code = TextField()
	is_read = BooleanField()