from django.shortcuts import render
from .models import Student
from .marklogic_utils import create_student, get_students

def create_student_view(request):
    # Create a sample student
    student_data = {"first_name": "Johna", "last_named": "Doe", "age": 22}
    created_student = create_student(student_data)
    print('created_student: ', created_student)

    return render(request, 'create_student.html', {'created_student': created_student})

def list_students_view(request):
    # Retrieve the list of students
    students = get_students()

    return render(request, 'list_students.html', {'students': students})