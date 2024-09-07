# yourapp/marklogic_utils.py
from marklogic import Client

def insert_data(data, collection="/student"):
    client = Client("http://localhost:8000", digest=("root", "root"))

    # Specify the collection where you want to store the data
    headers = {"Content-Type": "application/json", "Collection": collection}
    # response = client.put("/v1/documents?uri=/data.json", json=student_data)

    # Adjust the endpoint and use POST method to create a new document
    response = client.put("/v1/documents?uri=/data.json", json=data, headers=headers)

    return response.json()

data_to_insert = {
    "name": "John Doe",
    "age": 25,
    "city": "Example City Updated"
}

# Specify the collection where you want to store the data
collection_name = "/student"

# Insert the data into MarkLogic
result = insert_data(data_to_insert, collection=collection_name)

print("Result:", result)