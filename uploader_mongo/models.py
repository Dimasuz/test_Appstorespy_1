import datetime

from mongoengine import connect, Document, FileField, DateTimeField, LongField

connect('db_mongo', host='localhost', port=27017, username='ddd', password='123')


class UploadFileMongo(Document):
    file = FileField(required=True)
    uploaded_on = DateTimeField(default=datetime.datetime.utcnow, required=True)
    user = LongField(required=True)
