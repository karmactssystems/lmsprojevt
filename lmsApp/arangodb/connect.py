from pyArango.connection import Connection

connection = Connection(
    arangoURL='http://localhost:8529',  # Adjust the host and port as needed
    username='root',
    password='root',
)
db = connection['Testdb']
