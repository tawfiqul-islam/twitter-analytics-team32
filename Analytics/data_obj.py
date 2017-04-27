from couchdb.mapping import Document, TextField, IntegerField, DateTimeField, BooleanField

class TweetData(Document):
	_id = TextField()
	original_text = TextField()
	text = TextField()
	no_spell_text = TextField()
	label = IntegerField()
	tfid_features = TextField()
	features = TextField()
	geo_code = TextField()
	is_read = BooleanField()
	has_processed = BooleanField()