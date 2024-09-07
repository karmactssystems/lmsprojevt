# views.py

from django.shortcuts import get_object_or_404
from lmsApp.arangodb.arango_utils import connect_to_arangodb, create_document, get_document_by_id, update_document_by_id, delete_document_by_id
import json

# Connect to ArangoDB
db = connect_to_arangodb('Testdb', 'root', 'root')

# Create
def create_item(collection_name, data):
    collection = db[collection_name]
    create_document(collection, data)

# Read
def get_item_by_id(collection_name, item_id):
    collection = db[collection_name]
    return get_document_by_id(collection, item_id)

# Update
def update_item_by_id(collection_name, item_id, new_data):
    collection = db[collection_name]
    update_document_by_id(collection, item_id, new_data)

# Delete
def delete_item_by_id(collection_name, item_id):
    collection = db[collection_name]
    delete_document_by_id(collection, item_id)


def get_all_items(collection_name):
    collection = db[collection_name]
    items = list(collection.fetchAll())  # Retrieve all documents from the collection
    return items

def serialize_to_json(items):
    # Serialize the list of documents to JSON format
    json_data = json.dumps([item._createDict() for item in items], default=str)
    return json_data

def create_collections(collection_name):
        collection = db.create_collection(collection_name)
        print(f"Collection '{collection_name}' created with id: {collection.id}")
def get_paginated_data(collection_name,limit,offset):
    aql_query = f"""
    FOR doc IN {collection_name}
    SORT doc._key ASC
    LIMIT {offset} , {limit}
    RETURN doc
"""
    cursor = db.AQLQuery(aql_query,rawResults=True)
    return cursor

def update_all_status(collection_name, status):
    aql_query = f"""
    FOR doc IN {collection_name}
        UPDATE doc WITH {{ status: {str(status)} }} IN {collection_name}
    """
    cursor = db.AQLQuery(aql_query, rawResults=True)
    return cursor
def get_count(collection_name, status=None):
    aql_query=""
    if status is None:
        aql_query = f"""
    RETURN LENGTH(
        FOR doc IN {collection_name}
            RETURN doc
    )
    """
        cursor = db.AQLQuery(aql_query, rawResults=True)
    
    
    else:
        aql_query = f"""
        RETURN LENGTH(
            FOR doc IN {collection_name}
                FILTER doc.status == @status
                RETURN doc
        )
        """
        cursor = db.AQLQuery(aql_query, bindVars={'status': status}, rawResults=True)
        
    return cursor[0] if cursor else 0


def get_teachers():
    collection_name = 'Users'
    aql_query = f"""
    FOR user IN {collection_name}
    FILTER user.user_type == 'Teachers'
    RETURN {{
        id: user._id,
        first_name: user.first_name,
        last_name: user.last_name
    }}
    """
    cursor = db.AQLQuery(aql_query, rawResults=True)
    return cursor
