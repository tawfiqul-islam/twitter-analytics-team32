from couchdb.mapping import Document, TextField, IntegerField, DictField, DateTimeField, BooleanField

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
	coordinates = TextField()
	columns = DictField()
	lga_code = IntegerField()
	tag_food = BooleanField()
	tag_politic = BooleanField()