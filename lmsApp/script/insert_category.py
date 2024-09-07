import json
from lmsApp.arangodb.views.views import create_item, get_item_by_id, update_item_by_id,delete_item_by_id,get_all_items,serialize_to_json
from django.conf import settings
project_base_dir = settings.BASE_DIR
import os
import csv
import datetime


# Get the current working directory
current_directory = os.getcwd()

# Specify the file name (replace 'your_file.txt' with the actual file name)

# Join the current directory and file name to get the full path


def insert_data_from_json(file_path):
    full_path = os.path.join(current_directory,'lmsApp','script', file_path)
    print(full_path,"full_path")
    with open(full_path, 'r') as file:
        
        data = json.load(file)
        for entry in data:
            row = {
                "name": entry["name"],
                "description": entry["description"],
                "status": '1'  # Add your status logic here
            }
            create_item('Category',row)

# if __name__ == "__main__":
#     json_file_path = 'sub_category.json'
#     insert_data_from_json(json_file_path)

def insert_book_data(file_path):
    full_path = os.path.join(current_directory,'lmsApp','script', file_path)
    
    with open(full_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Map CSV fields to ArangoDB collection fields
            data = {
                "isbn": row["isbn"],
                "title": row["title"],
                "description": "",  # Add your description logic here
                "author": row["authors"],
                "publisher": row["publisher"],
                "date_published": row["publication_date"],
                "status": '1'  # Add your status logic here
            }

            # Insert data into ArangoDB collection
            create_item('Books',data)


def insert_user_data(file_path):
    full_path = os.path.join(current_directory,'lmsApp','script', file_path)
    
    with open(full_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Map CSV fields to ArangoDB collection fields
            data = {

                "code": row['User Id'],
                "first_name": row['First Name'],
                "last_name": row['Last Name'],
                "gender": 'Male',
                "contact": row['Phone'],
                "email": row['Email'],
                "department": row['Department'],
                "course": 'Computer Science',
                "address": row['Address'],
                "status": '1',
                "user_type": row['User Type'],
            }
            # Insert data into ArangoDB collection
            create_item('Users',data)


def insert_supplier_data(file_path):
    full_path = os.path.join(current_directory, 'lmsApp', 'script', file_path)

    with open(full_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Map CSV fields to ArangoDB collection fields
            data = {
                "supplier_no": row["Supplierno"],
                "name": row["Name"],
                "office_address": row["Address"],
                "mobile_no": row["Mobile No"],
                "email_id": row["Email"],

            }
            # Insert data into ArangoDB collection
            create_item('Supplier', data)
