
from pyArango.connection import Connection
from pyArango.collection import Collection, Edges

# Connect to ArangoDB
def connect_to_arangodb(db_name, username, password, host='http://localhost:8529'):
    connection = Connection(
        arangoURL=host,
        username=username,
        password=password,
    )
    return connection[db_name]

# Create Document in a Collection
def create_document(collection, data):
    new_document = collection.createDocument()
    for key, value in data.items():
        new_document[key] = value
    new_document.save()

# Read Document from a Collection by ID
def get_document_by_id(collection, doc_id):
    return collection[doc_id]

# Update Document in a Collection by ID
def update_document_by_id(collection, doc_id, new_data):
    document = collection[doc_id]
    for key, value in new_data.items():
        document[key] = value
    document.save()

# Delete Document from a Collection by ID
def delete_document_by_id(collection, doc_id):
    document = collection[doc_id]
    document.delete()


