from marklogic import Client

def create_student(student_data):
    client = Client("http://localhost:8000", digest=("root", "root"))

    response = client.put("/v1/documents?uri=/data.json", json=student_data)
    print('response: ', response);
    return response.json()

def get_students():
    client = Client("http://localhost:8000", digest=("root", "root"))

    response = client.get("/v1/documents", params={"uri": "/students/"})
    return response.json()