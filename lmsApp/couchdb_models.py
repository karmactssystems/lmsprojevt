import couchdb
from django.conf import settings

class CouchDBModel:
    def __init__(self, data):
        self.data = data
        self.doc_id = None

    def save(self):
        """Save the document to CouchDB"""
        COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE['USER']}:{settings.COUCHDB_DATABASE['PASSWORD']}@127.0.0.1:5984/"
        server = couchdb.Server(COUCHDB_URL)

        db_name = settings.COUCHDB_DATABASE["NAME"]
        if db_name in server:
            db = server[db_name]
        else:
            db = server.create(db_name)

        # Insert document
        doc_id, rev = db.save(self.data)
        self.doc_id = doc_id
        return doc_id
