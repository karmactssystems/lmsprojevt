import datetime
from django.shortcuts import redirect, render
import json
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from lmsApp import models, forms
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from lmsApp.arangodb.views.views import create_item, get_item_by_id, update_item_by_id,delete_item_by_id,get_all_items,serialize_to_json,create_collections,get_paginated_data,update_all_status,get_count, get_users, get_books
from lmsApp.script.insert_category import insert_data_from_json,insert_book_data,insert_user_data,insert_supplier_data
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from lmsApp.arangodb.arango_utils import delete_document_by_id
from lmsApp.arangodb.connect import db

def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        'system_host' : abs_uri,
        'page_name' : '',
        'page_title' : '',
        'system_name' : 'Library Managament System',
        'topbar' : True,
        'footer' : True,
    }

    return context
    
def userregister(request):
    context = context_data(request)
    context['topbar'] = False
    context['footer'] = False
    context['page_title'] = "User Registration"
    if request.user.is_authenticated:
        return redirect("home-page")
    return render(request, 'register.html', context)

def save_register(request):
    resp={'status':'failed', 'msg':''}
    if not request.method == 'POST':
        resp['msg'] = "No data has been sent on this request"
    else:
        form = forms.SaveUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Account has been created succesfully")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.name}] {error}.")
            
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def update_profile(request):
    context = context_data(request)
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = forms.UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = forms.UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile-page")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)

@login_required
def update_password(request):
    context =context_data(request)
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = forms.UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile-page")
        else:
            context['form'] = form
    else:
        form = forms.UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)

# Create your views here.
def login_page(request):
    context = context_data(request)
    context['topbar'] = False
    context['footer'] = False
    context['page_name'] = 'login'
    context['page_title'] = 'Login'
    return render(request, 'login.html', context)

def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

@login_required
def home(request):
    context = context_data(request)
    context['page'] = 'home'
    context['page_title'] = 'Home'
    context['categories'] = get_count('Category','1')
    context['sub_categories'] = models.SubCategory.objects.filter(delete_flag = 0, status = 1).all().count()
    context['students'] = get_count('Users',None)
    context['books'] = get_count('Books','1')
    context['pending'] = models.Borrow.objects.filter(status = 1).all().count()
    context['pending'] = models.Borrow.objects.filter(status = 1).all().count()
    context['transactions'] = models.Borrow.objects.all().count()

    return render(request, 'home.html', context)

def logout_user(request):
    logout(request)
    return redirect('login-page')
    
@login_required
def profile(request):
    context = context_data(request)
    context['page'] = 'profile'
    context['page_title'] = "Profile"
    return render(request,'profile.html', context)

@login_required
def users(request):
    context = context_data(request)
    context['page'] = 'users'
    context['page_title'] = "User List"
    context['users'] = User.objects.exclude(pk=request.user.pk).filter(is_superuser = False).all()
    return render(request, 'users.html', context)

@login_required
def save_user(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            user = User.objects.get(id = post['id'])
            form = forms.UpdateUser(request.POST, instance=user)
        else:
            form = forms.SaveUser(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "User has been saved successfully.")
            else:
                messages.success(request, "User has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def manage_user(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_user'
    context['page_title'] = 'Manage User'
    if pk is None:
        context['user'] = {}
    else:
        context['user'] = User.objects.get(id=pk)
    
    return render(request, 'manage_user.html', context)

@login_required
def delete_user(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'User ID is invalid'
    else:
        try:
            User.objects.filter(pk = pk).delete()
            messages.success(request, "User has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting User Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")
@login_required
def category(request):
    context = context_data(request)
    context['page'] = 'category'
    context['page_title'] = "Category List"
    
    # Assuming 'Category' is the ArangoDB collection name
    context['category'] = get_all_items('Category')
    # return context['category']
    return render(request, 'category.html', context)
    
@login_required
def save_categorySS(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            category = models.Category.objects.get(id = post['id'])
            form = forms.SaveCategory(request.POST, instance=category)
        else:
            form = forms.SaveCategory(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Category has been saved successfully.")
            else:
                messages.success(request, "Category has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")
@login_required
def save_category(request):
    resp = {'status': 'failed', 'msg': ''}
    
    if request.method == 'POST':
        form = forms.SaveCategory(request.POST)        
        if form.is_valid():
            print(request.POST,"request.POST")
            data = form.cleaned_data
            category_id = request.POST.get('id', '')
            if category_id:
                update_item_by_id('Category', category_id, data)  # Update the existing document
                messages.success(request, "Category has been updated successfully.")
            else:
                create_item('Category', data)  # Create a new document
                messages.success(request, "Category has been saved successfully.")
            
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg']:
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")
@login_required
def view_category(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_category'
    context['page_title'] = 'View Category'
    if pk is None:
        context['category'] = {}
    else:
        context['category'] = get_item_by_id("Category",pk)
    
    return render(request, 'view_category.html', context)

@login_required
def manage_category(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_category'
    context['page_title'] = 'Manage Category'
    if pk is None:
        context['category'] = {}
    else:
        context['category'] =get_item_by_id("Category",pk)
    
    return render(request, 'manage_category.html', context)

@login_required
def delete_category(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}

    print(f"Delete request for Category ID: {pk}")  # Debugging: print the ID to be deleted
    
    # Check if pk is valid
    if pk is None or pk == 'None':
        resp['msg'] = 'Invalid Category ID'
    else:
        try:
            # Delete item from ArangoDB instead of using Django models
            delete_item_by_id('Category', pk)  # Replace Django ORM deletion with ArangoDB function
            
            messages.success(request, "Category has been deleted successfully.")
            resp['status'] = 'success'
        except Exception as e:
            print(f"Error while deleting Category: {e}")  # Print exception for better debugging
            resp['msg'] = "Deleting Category Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def sub_category(request):
    context = context_data(request)
    context['page'] = 'sub_category'
    context['page_title'] = "Sub Category List"
    context['sub_category'] = get_all_items('SubCategory')
    return render(request, 'sub_category.html', context)

@login_required
def sub_category(request):
    context = context_data(request)
    context['page'] = 'sub_category'
    context['page_title'] = "Sub Category List"
    context['sub_category'] = get_all_items('SubCategory')
    return render(request, 'sub_category.html', context)

@login_required
def supplier_list(request):
    context = context_data(request)
    context['page'] = 'supplier'
    context['page_title'] = "Supplier List"
    context['supplier'] = get_all_items('Supplier')
    return render(request, 'supplier.html', context)

@login_required
def save_sub_category(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        form = forms.SaveSubCategory(request.POST) 
        if form.is_valid():
            data = form.cleaned_data
            post_id = post['id']
            print(type (post_id))
            if post['id'] != 'None':
                print(post['id'],"iddd")
                update_item_by_id('SubCategory',post['id'],data)
                messages.success(request, "Sub Category has been updated successfully.")       
            else:
                create_item("SubCategory",data)
                messages.success(request, "Sub Category has been saved successfully.")

        resp['status'] = 'success'
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_sub_category(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_sub_category'
    context['page_title'] = 'View Sub Category'
    if pk is None:
        context['sub_category'] = {}
    else:
        context['sub_category'] = get_item_by_id('SubCategory',pk)
    
    return render(request, 'view_sub_category.html', context)

@login_required
def manage_sub_category(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_sub_category'
    context['page_title'] = 'Manage Sub Category'
    if pk is None:
        context['sub_category'] = {}
    else:
        context['sub_category'] = get_item_by_id('SubCategory',pk)
    context['categories'] = get_all_items('Category')
    return render(request, 'manage_sub_category.html', context)

@login_required
def manage_supplier(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_supplier'
    context['page_title'] = 'Manage Supplier'
    if pk is None:
        context['supplier'] = {}
    else:
        context['supplier'] = get_item_by_id('Supplier',pk)
    return render(request, 'manage_supplier.html', context)

@login_required
def delete_sub_category(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Sub Category ID is invalid'
    else:
        try:
            models.SubCategory.objects.filter(pk = pk).update(delete_flag = 1)
            messages.success(request, "Sub Category has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Sub Category Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def books(request):
    context = context_data(request)
    context['page'] =  'book'
    context['page_title'] = "Book List"
    # context['books'] = models.Books.objects.filter(delete_flag = 0).all()
    limit_per_page = 100
    page_number = 1  # Change this based on the desired page number

    offset = (page_number - 1) * limit_per_page
    listdata = []
    for i in range(20):
        listdata = listdata + list(get_paginated_data('Books',limit_per_page,offset=offset))
    context['books'] = listdata
    print(context['books'])
    return render(request, 'books.html', context)

@login_required
def save_book(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        form = forms.SaveBook(request.POST) 
        if form.is_valid():
            data = form.cleaned_data
            print(post['id'],"postid")
            if post['id'] == 'None' or post['id'] == '':
                create_item('Books',data)
                messages.success(request, "Book has been saved successfully.")
            else:
                update_item_by_id('Books',post['id'],data)
                messages.success(request, "Book has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_book(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_book'
    context['page_title'] = 'View Book'
    if pk is None:
        context['book'] = {}
    else:
        context['book'] = get_item_by_id('Books',pk)
    
    return render(request, 'view_book.html', context)

@login_required
def manage_book(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_book'
    context['page_title'] = 'Manage Book'
    if pk is None:
        context['book'] = {}
    else:
        context['book'] = get_item_by_id('Books',pk)
    context['sub_categories'] = get_all_items('Category')
    print(context['sub_categories'])
    return render(request, 'manage_book.html', context)

@login_required
def delete_book(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}

    print(f"Delete request for Book ID: {pk}")  # Debugging: print the ID to be deleted
    
    # Check if pk is valid
    if pk is None or pk == 'None':
        resp['msg'] = 'Invalid Book ID'
    else:
        try:
            # Delete item from ArangoDB instead of using Django models
            delete_item_by_id('Books', pk)  # Replace Django ORM deletion with ArangoDB function
            
            messages.success(request, "Book has been deleted successfully.")
            resp['status'] = 'success'
        except Exception as e:
            print(f"Error while deleting Book: {e}")  # Print exception for better debugging
            resp['msg'] = "Deleting Book Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def students(request):
    context = context_data(request)
    context['page'] = 'student'
    context['page_title'] = "Student List"
    # context['students'] = models.Students.objects.filter(delete_flag = 0).all()
    
    limit_per_page = 100
    page_number = 1  # Change this based on the desired page number

    offset = (page_number - 1) * limit_per_page
    listdata = []
    for i in range(20):
        listdata = listdata + list(get_paginated_data('Users',limit_per_page,offset=offset))
    context['students'] = listdata
    return render(request, 'students.html', context)


@login_required
def save_student(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        form = forms.UserForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            if post['id'] == '' or post['id'] == 'None':
                create_item('Users',data)
                messages.success(request, "Student has been saved successfully.")
                
            else:
                update_item_by_id('Users',post['id'],data)
                messages.success(request, "Student has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_student(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_student'
    context['page_title'] = 'View Student'
    if pk is None:
        context['student'] = {}
    else:
        context['student'] = get_item_by_id('Users',pk)
    
    return render(request, 'view_student.html', context)

@login_required
def manage_student(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_student'
    context['page_title'] = 'Manage Student'
    if pk is None:
        context['student'] = {}
    else:
        context['student'] =get_item_by_id('Users',pk)
    context['sub_categories'] = get_all_items('SubCategory')
    context['user_types']=['Students','Teachers']
    return render(request, 'manage_student.html', context)

@login_required
def delete_student(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Student ID is invalid'
    else:
        try:
            models.Students.objects.filter(pk = pk).update(delete_flag = 1)
            messages.success(request, "Student has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Student Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")



@login_required
def get_borrows(request):
    context = context_data(request)
    context['page'] = 'borrow'
    context['page_title'] = "Borrowing Transaction"
    
    # Assuming 'Category' is the ArangoDB collection name
    context['borrows'] = get_all_items('Borrow')
    return render(request, 'borrows.html', context)


@login_required
def save_borrow(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        form = forms.SaveBorrow(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            borrow_id = request.POST.get('pk', '')

            if borrow_id:
                update_item_by_id('Borrow', borrow_id, data)  # Update
                messages.success(request, "Borrow Transaction has been updated successfully.")
            else:
                create_item('Borrow', data)  # Create
                messages.success(request, "Borrow Transaction has been saved successfully.")

            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg']:
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "No data sent in the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")



@login_required
def manage_borrow(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_borrow'
    context['page_title'] = 'Manage User Information'
    context['users'] = get_users()
    print(context['users'])
    context['books'] = get_books()
    print(context['books'])    

    if pk is None:
        context['borrow'] = {}
    else:
        user_info = get_item_by_id("Borrow", pk)
        context['borrow'] = user_info
        if 'due_date' in user_info:
            # Ensure join_date is in YYYY-MM-DD format
            try:
                due_date = datetime.strptime(user_info['due_date'], '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                due_date = ''  # or handle the error appropriately
            user_info['due_date'] = due_date
        if 'borrowing_date' in user_info:
            # Ensure join_date is in YYYY-MM-DD format
            try:
                borrowing_date = datetime.strptime(user_info['borrowing_date'], '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                borrowing_date = ''  # or handle the error appropriately
            user_info['borrowing_date'] = borrowing_date
        if 'return_date' in user_info:
            # Ensure join_date is in YYYY-MM-DD format
            try:
                return_date = datetime.strptime(user_info['return_date'], '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                return_date = ''  # or handle the error appropriately
            user_info['return_date'] = return_date
        
    return render(request, 'manage_borrow.html', context)


@login_required
def view_borrow(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_borrow'
    context['page_title'] = 'View User Information'
    if pk is None:
        context['borrow'] = {}
    else:
        context['borrow'] = get_item_by_id("Borrow",pk)
    return render(request, 'view_borrow.html', context)

@login_required
def delete_borrow(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}

    print(f"Delete request for Borrow ID: {pk}")  # Debugging: print the ID to be deleted
    
    # Check if pk is valid
    if pk is None or pk == 'None':
        resp['msg'] = 'Invalid Borrow ID'
    else:
        try:
            # Delete item from ArangoDB instead of using Django models
            delete_item_by_id('Borrow', pk)  # Replace Django ORM deletion with ArangoDB function
            
            messages.success(request, "Borrow Transaction has been deleted successfully.")
            resp['status'] = 'success'
        except Exception as e:
            print(f"Error while deleting Borrow: {e}")  # Print exception for better debugging
            resp['msg'] = "Deleting Borrow Transaction Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def save_supplier(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        form = forms.SaveSupplier(request.POST) 
        if form.is_valid():
            data = form.cleaned_data
            if post['id'] == '':
                create_item('Supplier',data)
                messages.success(request, "Supplier has been saved successfully.")
            else:
                update_item_by_id('Supplier',post['id'],data)
                messages.success(request, "Supplier has been updated successfully.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

def insert_dummy_data(request):
    message = request.GET.get('message')
    model = request.GET.get('model')
    collection_name = request.GET.get('collection_name')
    status = request.GET.get('status')
    if model == 'book':
        insert_book_data('books.csv')
    elif model == 'user':
        insert_user_data('users.csv')
    elif model == 'supplier':
        insert_supplier_data('Supplier.csv')
    elif model == 'category':
        insert_data_from_json('sub_category.json')
   
    if collection_name: 
        update_all_status(collection_name,status)  
        
    return HttpResponse(json.dumps({'category': message}), content_type="application/json")


def create_arango_collections(request):
    list=['Users','Category','SubCategory','Books',"NewCollection"]
    for i in list:
        create_collections(i)
    return HttpResponse(json.dumps({'Collections': list}), content_type="application/json")


@login_required
def get_teaching_materials(request):
    context = context_data(request)
    context['page'] = 'teaching_material'
    context['page_title'] = "Teaching Materials"
    
    context['teaching_material'] = get_all_items('TeachingMaterial')  # Fetch all materials
    return render(request, 'teaching_material.html', context)

import os
from django.conf import settings
from django.core.files.storage import default_storage

@login_required
def save_teaching_material(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        form = forms.SaveTeachingMaterial(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            teaching_material_id = request.POST.get('id', '')

            # Handle file saving
            teaching_reference_file = request.FILES.get('teaching_reference')
            if teaching_reference_file:
                # Save the file and get the path
                file_path = default_storage.save(
                    os.path.join('teaching_materials', teaching_reference_file.name),
                    teaching_reference_file
                )
                data['teaching_reference'] = teaching_reference_file.name

            if teaching_material_id:
                update_item_by_id('TeachingMaterial', teaching_material_id, data)  # Update
                messages.success(request, "Teaching Material has been updated successfully.")
            else:
                create_item('TeachingMaterial', data)  # Create
                messages.success(request, "Teaching Material has been saved successfully.")

            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg']:
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "No data sent in the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

# views.py
from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os
import urllib.parse

@login_required
def download_file(request, file_key):
    try:
        # Decode the file_key from URL encoding
        decoded_file_key = urllib.parse.unquote(file_key)

        # Construct the file path relative to MEDIA_ROOT
        file_path = os.path.join(settings.MEDIA_ROOT, 'teaching_materials', decoded_file_key)

        # Check if the file exists
        if not os.path.exists(file_path):
            raise Http404("File does not exist")

        # Open and serve the file
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/force-download')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(decoded_file_key)}"'
            response['Content-Length'] = os.path.getsize(file_path)
            return response

    except Exception as e:
        print(f"Error: {e}")  # Log the error
        raise Http404("An error occurred while downloading the file")


@login_required
def manage_teaching_material(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_teaching_material'
    context['page_title'] = 'Manage Teaching Material'

    if pk is None:
        context['teaching_material'] = {}
    else:
        context['teaching_material'] =get_item_by_id("TeachingMaterial",pk)

        print(context['teaching_material'])
    # context['subject'] = ['Electronics', 'Computer Science']
    # context['course'] = ['BCA', 'BSC', 'FYBCom']
    return render(request, 'manage_teaching_material.html', context)

@login_required
def view_teaching_material(request, pk=None):
    context = context_data(request)
    context['page'] = 'view_teaching_material'
    context['page_title'] = 'View Teaching Materials'

    if pk is not None:
        context['teaching_material'] = get_item_by_id("TeachingMaterial", pk)  # Fetch by ID
    
    return render(request, 'view_teaching_material.html', context)

@login_required
def delete_teaching_material(request, pk):
    resp = {'status': 'failed', 'msg': ''}
    
    if request.method == 'POST':
        # Ensure the ID is provided
        if not pk:
            resp['msg'] = 'No ID provided'
            return HttpResponse(json.dumps(resp), content_type="application/json")
        
        # Try to delete the item from ArangoDB
        try:
            delete_item_by_id('TeachingMaterial', pk)
            resp['status'] = 'success'
            resp['msg'] = 'Teaching Material has been deleted successfully.'
        except Exception as e:
            resp['msg'] = str(e)  # Capture and return any errors
        
    else:
        resp['msg'] = 'Invalid request method. Only POST is allowed.'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")



@login_required
def get_user_info(request):
    context = context_data(request)
    context['page'] = 'user_info'
    context['page_title'] = "User Information"
    
    # Assuming 'Category' is the ArangoDB collection name
    context['user_infos'] = get_all_items('UserInfo')
    # return context['category']
    return render(request, 'user_info.html', context)


@login_required
def save_user_info(request):
    resp = {'status': 'failed', 'msg': ''}

    if request.method == 'POST':
        form = forms.SaveUserInfo(request.POST)  # Include request.FILES
        if form.is_valid():
            print(request.POST, "request.POST")
            data = form.cleaned_data
            category_id = request.POST.get('id', '')
            if category_id:
                update_item_by_id('UserInfo', category_id, data)  # Update the existing document
                messages.success(request, "Teaching Material has been updated successfully.")
            else:
                create_item('UserInfo', data)  # Create a new document
                messages.success(request, "Teaching Material has been saved successfully.")

            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg']:
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
        resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def manage_user_info(request, pk=None):
    context = context_data(request)
    context['page'] = 'manage_user_info'
    context['page_title'] = 'Manage User Information'
    
    if pk is None:
        context['user_info'] = {}
    else:
        user_info = get_item_by_id("UserInfo", pk)
        if 'join_date' in user_info:
            # Ensure join_date is in YYYY-MM-DD format
            try:
                join_date = datetime.strptime(user_info['join_date'], '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                join_date = ''  # or handle the error appropriately
            user_info['join_date'] = join_date
        context['user_info'] = user_info
        print(context['user_info'])
    
    return render(request, 'manage_user_info.html', context)


@login_required
def view_user_info(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_user_info'
    context['page_title'] = 'View User Information'
    if pk is None:
        context['user_info'] = {}
    else:
        context['user_info'] = get_item_by_id("UserInfo",pk)
    return render(request, 'view_user_info.html', context)

@login_required
def delete_user_info(request, pk=None):
    resp = {'status': 'failed', 'msg': ''}

    print(f"Delete request for UserInfo ID: {pk}")  # Debugging: print the ID to be deleted
    
    # Check if pk is valid
    if pk is None or pk == 'None':
        resp['msg'] = 'Invalid User Info ID'
    else:
        try:
            # Delete item from ArangoDB instead of using Django models
            delete_item_by_id('UserInfo', pk)  # Replace Django ORM deletion with ArangoDB function
            
            messages.success(request, "User Info has been deleted successfully.")
            resp['status'] = 'success'
        except Exception as e:
            print(f"Error while deleting UserInfo: {e}")  # Print exception for better debugging
            resp['msg'] = "Deleting User Info Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")




import couchdb
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import StudentForm, TeacherForm, SubCategoryForm, BooksForm, JournalForm, SupplierForm

def create_student_couch(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            # Connect to CouchDB
            COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE['USER']}:{settings.COUCHDB_DATABASE['PASSWORD']}@127.0.0.1:5984/"
            server = couchdb.Server(COUCHDB_URL)

            db_name = settings.COUCHDB_DATABASE["NAME"]
            if db_name in server:
                db = server[db_name]
            else:
                db = server.create(db_name)

            # Save Student Record
            student_data = form.cleaned_data
            doc_id, _ = db.save(student_data)

            return redirect("student_list_couch")  # Redirect to student list page (to be created)

    else:
        form = StudentForm()
    
    return render(request, "create_student.html", {"form": form})



def student_list_couch(request):
    # Connect to CouchDB
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE['USER']}:{settings.COUCHDB_DATABASE['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve all student documents
    students = []
    for doc_id in db:
        student_doc = db[doc_id]
        students.append({
            "id": doc_id,
            "name": f"{student_doc.get('first_name', '')} {student_doc.get('last_name', '')}",
            "email": student_doc.get("email", ""),
            "gender": student_doc.get("gender", ""),
            "contact": student_doc.get("contact", ""),
            "address": student_doc.get("address", ""),
            "department": student_doc.get("department", ""),
            "course": student_doc.get("course", ""),
            "status": student_doc.get("status", ""),
            "code": student_doc.get("code", ""),
        })

    return render(request, "student_list_couch.html", {"students": students})


# View to edit a student document
def edit_student_couch(request, student_id):
    # Connect to CouchDB
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE['USER']}:{settings.COUCHDB_DATABASE['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the student document by ID
    student_doc = db.get(student_id)
    if not student_doc:
        return redirect("student_list_couch")

    # Pre-fill the form with the current student data
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            # Update the document with new data
            student_data = form.cleaned_data
            student_doc.update(student_data)
            db.save(student_doc)  # Save the updated document

            return redirect("student_list_couch")
    else:
        form = StudentForm(initial=student_doc)  # Pre-fill the form

    return render(request, "edit_student.html", {"form": form, "student_id": student_id})

# View to delete a student document
def delete_student_couch(request, student_id):
    # Connect to CouchDB
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE['USER']}:{settings.COUCHDB_DATABASE['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Delete the student document by ID
    student_doc = db.get(student_id)
    if student_doc:
        db.delete(student_doc)  # Delete the document

    return redirect("student_list_couch")


def create_teacher_couch(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            # Connect to CouchDB
            COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE2['USER']}:{settings.COUCHDB_DATABASE2['PASSWORD']}@127.0.0.1:5984/"
            server = couchdb.Server(COUCHDB_URL)

            db_name = settings.COUCHDB_DATABASE2["NAME"]
            if db_name in server:
                db = server[db_name]
            else:
                db = server.create(db_name)

            # Save Teacher Record
            teacher_data = form.cleaned_data
            doc_id, _ = db.save(teacher_data)

            return redirect("teacher_list_couch")  # Redirect to teacher list page

    else:
        form = TeacherForm()
    
    return render(request, "create_teacher.html", {"form": form})


# Teacher List
def teacher_list_couch(request):
    # Connect to CouchDB
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE2['USER']}:{settings.COUCHDB_DATABASE2['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE2["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve all teacher documents
    teachers = []
    for doc_id in db:
        teacher_doc = db[doc_id]
        teachers.append({
            "id": doc_id,
            "name": f"{teacher_doc.get('first_name', '')} {teacher_doc.get('last_name', '')}",
            "email": teacher_doc.get("email", ""),
            "gender": teacher_doc.get("gender", ""),
            "contact": teacher_doc.get("contact", ""),
            "address": teacher_doc.get("address", ""),
            "department": teacher_doc.get("department", ""),
            "course": teacher_doc.get("course", ""),
            "status": teacher_doc.get("status", ""),
        })

    return render(request, "teacher_list_couch.html", {"teachers": teachers})


# Edit Teacher
def edit_teacher_couch(request, teacher_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE2['USER']}:{settings.COUCHDB_DATABASE2['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE2["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the teacher document
    teacher_doc = db.get(teacher_id)
    if not teacher_doc:
        return redirect("teacher_list_couch")

    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            # Update Teacher Record
            teacher_data = form.cleaned_data
            teacher_doc.update(teacher_data)
            db[teacher_id] = teacher_doc  # Save updated document

            return redirect("teacher_list_couch")
    else:
        form = TeacherForm(initial=teacher_doc)

    return render(request, "edit_teacher_couch.html", {"form": form})


# Delete Teacher
def delete_teacher_couch(request, teacher_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE2['USER']}:{settings.COUCHDB_DATABASE2['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE2["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the teacher document
    teacher_doc = db.get(teacher_id)
    if teacher_doc:
        db.delete(teacher_doc)  # Delete the document

    return redirect("teacher_list_couch")


def create_sub_category_couch(request):
    if request.method == "POST":
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            # Connect to CouchDB
            COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE3['USER']}:{settings.COUCHDB_DATABASE3['PASSWORD']}@127.0.0.1:5984/"
            server = couchdb.Server(COUCHDB_URL)

            db_name = settings.COUCHDB_DATABASE3["NAME"]
            if db_name in server:
                db = server[db_name]
            else:
                db = server.create(db_name)

            # Save Teacher Record
            teacher_data = form.cleaned_data
            doc_id, _ = db.save(teacher_data)

            return redirect("sub_category_list_couch")  # Redirect to teacher list page

    else:
        form = SubCategoryForm()
    
    return render(request, "create_sub_category_couch.html", {"form": form})

def sub_category_list_couch(request):
    # Connect to CouchDB
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE3['USER']}:{settings.COUCHDB_DATABASE3['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE3["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve all sub-category documents
    sub_categories = []
    for doc_id in db:
        sub_category_doc = db[doc_id]
        status_code = sub_category_doc.get("status", "1")  # Default to 'Active' if status is missing

        # Map the status code to a human-readable label
        status_label = "Active" if status_code == "1" else "Inactive"

        sub_categories.append({
            "id": doc_id,
            "name": sub_category_doc.get("name", ""),
            "description": sub_category_doc.get("description", ""),
            "status": status_label,
        })

    return render(request, "sub_category_list_couch.html", {"sub_categories": sub_categories})



def edit_sub_category_couch(request, sub_category_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE3['USER']}:{settings.COUCHDB_DATABASE3['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE3["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the teacher document
    sub_category_doc = db.get(sub_category_id)
    if not sub_category_doc:
        return redirect("sub_category_list_couch")
    
    if request.method == "POST":
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            # Update Teacher Record
            sub_category_data = form.cleaned_data
            sub_category_doc.update(sub_category_data)
            db[sub_category_id] = sub_category_doc

            return redirect("sub_category_list_couch")
        
    else:
        form = SubCategoryForm(initial=sub_category_doc)
    
    return render(request, "edit_sub_category_couch.html", {"form": form})


def delete_sub_category_couch(request, sub_category_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE3['USER']}:{settings.COUCHDB_DATABASE3['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE3["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the teacher document
    sub_category_doc = db.get(sub_category_id)
    if sub_category_doc:
        db.delete(sub_category_doc)  # Delete the document

    return redirect("sub_category_list_couch")



def create_book(request):
    if request.method == "POST":
        form = BooksForm(request.POST)
        if form.is_valid():
            # Connect to CouchDB
            COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE4['USER']}:{settings.COUCHDB_DATABASE4['PASSWORD']}@127.0.0.1:5984/"
            server = couchdb.Server(COUCHDB_URL)

            db_name = settings.COUCHDB_DATABASE4["NAME"]
            if db_name in server:
                db = server[db_name]
            else:
                db = server.create(db_name)

            # Save Book Record
            book_data = form.cleaned_data
            doc_id, _ = db.save(book_data)

            return redirect("book_list_couch")  # Redirect to book list page

    else:
        form = BooksForm()

    return render(request, "create_book_couch.html", {"form": form})

# List Books
def book_list_couch(request):
    # Connect to CouchDB
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE4['USER']}:{settings.COUCHDB_DATABASE4['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE4["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve all book documents
    books = []
    for doc_id in db:
        book_doc = db[doc_id]
        status_code = book_doc.get("status", "1")  # Default to 'Active' if status is missing

        # Map the status code to a human-readable label
        status_label = "Active" if status_code == "1" else "Inactive"

        books.append({
            "id": doc_id,
            "isbn": book_doc.get("isbn", ""),
            "title": book_doc.get("title", ""),
            "description": book_doc.get("description", ""),
            "author": book_doc.get("author", ""),
            "publisher": book_doc.get("publisher", ""),
            "status": status_label,
        })

    return render(request, "book_list_couch.html", {"books": books})

# Edit Book
def edit_book_couch(request, book_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE4['USER']}:{settings.COUCHDB_DATABASE4['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE4["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the book document
    book_doc = db.get(book_id)
    if not book_doc:
        return redirect("book_list_couch")
    
    if request.method == "POST":
        form = BooksForm(request.POST)
        if form.is_valid():
            # Update Book Record
            book_data = form.cleaned_data
            book_doc.update(book_data)
            db[book_id] = book_doc

            return redirect("book_list_couch")
        
    else:
        form = BooksForm(initial=book_doc)
    
    return render(request, "edit_book_couch.html", {"form": form})

# Delete Book
def delete_book_couch(request, book_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE4['USER']}:{settings.COUCHDB_DATABASE4['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE4["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the book document
    book_doc = db.get(book_id)
    if book_doc:
        db.delete(book_doc)  # Delete the document

    return redirect("book_list_couch")


def create_journal_couch(request):
    if request.method == "POST":
        form = JournalForm(request.POST)
        if form.is_valid():
            # Connect to CouchDB
            COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE5['USER']}:{settings.COUCHDB_DATABASE5['PASSWORD']}@127.0.0.1:5984/"
            server = couchdb.Server(COUCHDB_URL)

            db_name = settings.COUCHDB_DATABASE5["NAME"]
            if db_name in server:
                db = server[db_name]
            else:
                db = server.create(db_name)

            # Save Book Record
            book_data = form.cleaned_data
            doc_id, _ = db.save(book_data)

            return redirect("journal_list_couch")  # Redirect to book list page

    else:
        form = JournalForm()

    return render(request, "create_journal_couch.html", {"form": form})


def journal_list_couch(request):
    # Connect to CouchDB
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE5['USER']}:{settings.COUCHDB_DATABASE5['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE5["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve all book documents
    books = []
    for doc_id in db:
        book_doc = db[doc_id]
        status_code = book_doc.get("status", "1")  # Default to 'Active' if status is missing

        # Map the status code to a human-readable label
        status_label = "Active" if status_code == "1" else "Inactive"

        books.append({
            "id": doc_id,
            "title": book_doc.get("title", ""),
            "description": book_doc.get("description", ""),
            "author": book_doc.get("author", ""),
            "publisher": book_doc.get("publisher", ""),
            "status": status_label,
        })

    return render(request, "journal_list_couch.html", {"books": books})

# Edit Book
def edit_journal_couch(request, book_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE5['USER']}:{settings.COUCHDB_DATABASE5['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE5["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the book document
    book_doc = db.get(book_id)
    if not book_doc:
        return redirect("journal_list_couch")
    
    if request.method == "POST":
        form = JournalForm(request.POST)
        if form.is_valid():
            # Update Book Record
            book_data = form.cleaned_data
            book_doc.update(book_data)
            db[book_id] = book_doc

            return redirect("journal_list_couch")
        
    else:
        form = JournalForm(initial=book_doc)
    
    return render(request, "edit_journal_couch.html", {"form": form})

# Delete Book
def delete_journal_couch(request, book_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE5['USER']}:{settings.COUCHDB_DATABASE5['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE5["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the book document
    book_doc = db.get(book_id)
    if book_doc:
        db.delete(book_doc)  # Delete the document

    return redirect("journal_list_couch")


def create_supplier_couch(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            # Connect to CouchDB
            COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE6['USER']}:{settings.COUCHDB_DATABASE6['PASSWORD']}@127.0.0.1:5984/"
            server = couchdb.Server(COUCHDB_URL)

            db_name = settings.COUCHDB_DATABASE6["NAME"]
            if db_name in server:
                db = server[db_name]
            else:
                db = server.create(db_name)

            # Save Book Record
            book_data = form.cleaned_data
            doc_id, _ = db.save(book_data)

            return redirect("supplier_list_couch")  # Redirect to book list page

    else:
        form = SupplierForm()

    return render(request, "create_supplier_couch.html", {"form": form})


def supplier_list_couch(request):
    # Connect to CouchDB
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE6['USER']}:{settings.COUCHDB_DATABASE6['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE6["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve all book documents
    books = []
    for doc_id in db:
        book_doc = db[doc_id]
        status_code = book_doc.get("status", "1")  # Default to 'Active' if status is missing

        # Map the status code to a human-readable label
        status_label = "Active" if status_code == "1" else "Inactive"

        books.append({
            "id": doc_id,
            "name": book_doc.get("name", ""),
            "email": book_doc.get("email", ""),
            "phone": book_doc.get("phone", ""),
            "address": book_doc.get("address", ""),
            "status": status_label,
        })

    return render(request, "supplier_list_couch.html", {"books": books})

# Edit Book
def edit_supplier_couch(request, book_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE6['USER']}:{settings.COUCHDB_DATABASE6['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE6["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the book document
    book_doc = db.get(book_id)
    if not book_doc:
        return redirect("supplier_list_couch")
    
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            # Update Book Record
            book_data = form.cleaned_data
            book_doc.update(book_data)
            db[book_id] = book_doc

            return redirect("supplier_list_couch")
        
    else:
        form = SupplierForm(initial=book_doc)
    
    return render(request, "edit_supplier_couch.html", {"form": form})

# Delete Book
def delete_supplier_couch(request, book_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE6['USER']}:{settings.COUCHDB_DATABASE6['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE6["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the book document
    book_doc = db.get(book_id)
    if book_doc:
        db.delete(book_doc)  # Delete the document

    return redirect("supplier_list_couch")


def create_material_couch(request):
    if request.method == "POST":
        form = TeachingMaterialForm(request.POST)
        if form.is_valid():
            # Connect to CouchDB
            COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE7['USER']}:{settings.COUCHDB_DATABASE7['PASSWORD']}@127.0.0.1:5984/"
            server = couchdb.Server(COUCHDB_URL)

            db_name = settings.COUCHDB_DATABASE7["NAME"]
            if db_name in server:
                db = server[db_name]
            else:
                db = server.create(db_name)

            # Save Book Record
            book_data = form.cleaned_data
            doc_id, _ = db.save(book_data)

            return redirect("material_list_couch")  # Redirect to book list page

    else:
        form = TeachingMaterialForm()

    return render(request, "create_material_couch.html", {"form": form})


def material_list_couch(request):
    # Connect to CouchDB
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE7['USER']}:{settings.COUCHDB_DATABASE7['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE7["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve all book documents
    books = []
    for doc_id in db:
        book_doc = db[doc_id]
        books.append({
            "id": doc_id,
            "name": book_doc.get("name", ""),
            "subject": book_doc.get("subject", ""),
            "course": book_doc.get("course", ""),
            "teaching_reference": book_doc.get("teaching_reference", ""),
        })
    print("Books", books)
    return render(request, "material_list_couch.html", {"books": books})

# Edit Book
def edit_material_couch(request, book_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE7['USER']}:{settings.COUCHDB_DATABASE7['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE7["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the book document
    book_doc = db.get(book_id)
    if not book_doc:
        return redirect("material_list_couch")
    
    if request.method == "POST":
        form = TeachingMaterialForm(request.POST)
        if form.is_valid():
            # Update Book Record
            book_data = form.cleaned_data
            book_doc.update(book_data)
            db[book_id] = book_doc

            return redirect("material_list_couch")
        
    else:
        form = TeachingMaterialForm(initial=book_doc)
    
    return render(request, "edit_material_couch.html", {"form": form})

# Delete Book
def delete_material_couch(request, book_id):
    COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE7['USER']}:{settings.COUCHDB_DATABASE7['PASSWORD']}@127.0.0.1:5984/"
    server = couchdb.Server(COUCHDB_URL)

    db_name = settings.COUCHDB_DATABASE7["NAME"]
    if db_name in server:
        db = server[db_name]
    else:
        db = server.create(db_name)

    # Retrieve the book document
    book_doc = db.get(book_id)
    if book_doc:
        db.delete(book_doc)  # Delete the document

    return redirect("material_list_couch")

from .models import TeachingMaterialSchema
from .forms import TeachingMaterialForm

# List View
def teaching_material_list_neo(request):
    materials = TeachingMaterialSchema.nodes.filter(delete_flag=0)
    return render(request, 'teaching_material_list_neo.html', {'materials': materials})

# Create View
import uuid
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage

def create_teaching_material_neo(request):
    if request.method == 'POST':
        form = TeachingMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle file saving
            teaching_reference_url = None
            if form.cleaned_data['teaching_reference']:
                file = form.cleaned_data['teaching_reference']
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                teaching_reference_url = fs.url(filename)

            # Create new teaching material instance
            material = TeachingMaterialSchema(
                name=form.cleaned_data['name'],
                subject=form.cleaned_data['subject'],
                course=form.cleaned_data['course'],
                teaching_reference=teaching_reference_url
            )
            if not material.uid:  # Ensure UID is not regenerated
                material.uid = uuid.uuid4().hex
            material.save()
            return redirect('teaching_material_list_neo')
    else:
        form = TeachingMaterialForm()
    
    return render(request, 'teaching_material_form_neo.html', {'form': form, 'title': 'Create Teaching Material Neo'})


# Update View
def update_teaching_material_neo(request, material_id):
    material = TeachingMaterialSchema.nodes.get_or_none(uid=material_id)
    if not material:
        return redirect('teaching_material_list_neo')

    if request.method == 'POST':
        form = TeachingMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            # Update fields
            material.name = form.cleaned_data['name']
            material.subject = form.cleaned_data['subject']
            material.course = form.cleaned_data['course']
            
            # Update the file if a new one is uploaded
            if form.cleaned_data['teaching_reference']:
                file = form.cleaned_data['teaching_reference']
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                material.teaching_reference = fs.url(filename)

            material.save()
            return redirect('teaching_material_list_neo')
    else:
        initial_data = {
            'name': material.name,
            'subject': material.subject,
            'course': material.course,
            'teaching_reference': material.teaching_reference,
        }
        form = TeachingMaterialForm(initial=initial_data)

    return render(request, 'teaching_material_form_neo.html', {'form': form, 'title': 'Update Teaching Material Neo'})


# Delete View
def delete_teaching_material_neo(request, material_id):
    material = TeachingMaterialSchema.nodes.get_or_none(uid=material_id)
    if material:
        material.delete_flag = 1  # Soft delete instead of removing from DB
        material.save()
    return redirect('teaching_material_list_neo')



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReviewForm
from .models import ReviewSchema, TeachingMaterialSchema
from django.http import Http404

# def create_review_neo(request):
#     # Get the TeachingMaterialSchema node by the passed UID

#     # If the material doesn't exist, raise a 404 error
#     form = ReviewForm(request.POST)
#     if request.method == 'POST':
#         if form.is_valid():
#             # Create the review using the provided data
#             review = ReviewSchema(
#                 review_text=form.cleaned_data['review_text'],
#                 rating=form.cleaned_data['rating'],
#                 reviewer_name=form.cleaned_data['reviewer_name'],
#             )
#             review.save()  # Save the review in Neo4j
#             return redirect('review_list_neo')  # Redirect to the review list
#     return render(request, 'create_review_neo.html', {'form': form, 'title': 'Create Review'})
def get_teaching_materials_options():
    """ Fetch teaching material names from CouchDB. """
    couch = couchdb.Server(settings.COUCHDB_DATABASE7["HOST"])
    couch.resource.credentials = (settings.COUCHDB_DATABASE7["USER"], settings.COUCHDB_DATABASE7["PASSWORD"])
    db = couch[settings.COUCHDB_DATABASE7["NAME"]]

    materials = []
    for doc_id in db:
        doc = db[doc_id]
        if "name" in doc:  # Ensure 'name' exists in the document
            materials.append({"id": doc_id, "name": doc["name"]})
    print("Fetched Materials:", materials)
    return materials

def create_review_neo(request):
    teaching_materials = get_teaching_materials_options()  # Fetch material names
    print("Teaching Materials:", teaching_materials)  # Debugging Output

    if request.method == 'POST':
        form = ReviewForm(request.POST, materials=teaching_materials)  # Pass materials here
        if form.is_valid():
            review = ReviewSchema(
                review_text=form.cleaned_data['review_text'],
                rating=form.cleaned_data['rating'],
                reviewer_name=form.cleaned_data['reviewer_name'],
                reviewed_material=form.cleaned_data['reviewed_material']
            )
            review.save()  # Save the review in Neo4j
            return redirect('review_list_neo')
    else:
        form = ReviewForm(materials=teaching_materials)  # ✅ Pass materials here

    return render(request, 'create_review_neo.html', {
        'form': form,
        'title': 'Create Review'
    })




# # List all reviews
def review_list_neo(request):
    # Fetch all reviews from Neo4j
    reviews = ReviewSchema.nodes.all()  # Replace Django's .objects with Neo4j's .nodes.all()

    return render(request, 'review_list_neo.html', {'reviews': reviews, 'title': 'Review List'})


# Update review
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404

def update_review_neo(request, review_uid):
    try:
        review = ReviewSchema.nodes.get(uid=review_uid)  # Corrected way to fetch
    except ReviewSchema.DoesNotExist:
        raise Http404("Review not found")

    if request.method == 'POST':
        form = ReviewForm(request.POST, initial={  # Populate with existing data
            'review_text': review.review_text,
            'rating': review.rating,
            'reviewer_name': review.reviewer_name,
            'reviewed_material': review.reviewed_material
        })
        if form.is_valid():
            review.review_text = form.cleaned_data['review_text']
            review.rating = form.cleaned_data['rating']
            review.reviewer_name = form.cleaned_data['reviewer_name']
            review.reviewed_material = form.cleaned_data['reviewed_material']
            review.save()
            return redirect('review_list_neo')  
    else:
        form = ReviewForm(initial={  # Prefill form for GET request
            'review_text': review.review_text,
            'rating': review.rating,
            'reviewer_name': review.reviewer_name,
            'reviewed_material': review.reviewed_material
        })

    return render(request, 'create_review_neo.html', {'form': form, 'title': 'Update Review'})

def delete_review_neo(request, review_uid):
    review = ReviewSchema.nodes.get_or_none(uid=review_uid)
    if review:
        review.delete()  # Hard delete; change this if soft delete is needed
    return redirect('review_list_neo')



from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReviewForm, FeedbackForm
from .models import ReviewSchema, TeachingMaterialSchema, FeedbackSchema
from django.http import Http404
from datetime import datetime

def create_feedback_neo(request):

    form = FeedbackForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            # Convert the feedback_date (which is a datetime.date object) to a datetime.datetime object
            feedback_date = form.cleaned_data['feedback_date']
            if feedback_date:
                # Convert to datetime (we're assuming the time is 00:00:00)
                feedback_date = datetime.combine(feedback_date, datetime.min.time())

            # Create the review using the provided data
            review = FeedbackSchema(
                feedback_text=form.cleaned_data['feedback_text'],
                feedback_date=feedback_date,  # Use the converted datetime.datetime
                feedback_giver=form.cleaned_data['feedback_giver'],
            )
            review.save()  # Save the review in Neo4j
            return redirect('feedback_list_neo')  # Redirect to the review list

    return render(request, 'create_feedback_neo.html', {'form': form, 'title': 'Create Feedback'})




# # List all reviews
def feedback_list_neo(request):
    # Fetch all reviews from Neo4j
    reviews = FeedbackSchema.nodes.all()  # Replace Django's .objects with Neo4j's .nodes.all()

    return render(request, 'feedback_list_neo.html', {'reviews': reviews, 'title': 'Review List'})


# # Update review
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import Http404
from .forms import FeedbackForm
from .models import FeedbackSchema  # Ensure this is your Neo4j schema

def update_feedback_neo(request, review_uid):
    review = FeedbackSchema.nodes.get_or_none(uid=review_uid)
    
    if not review:
        raise Http404("Review not found.")

    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            # Convert feedback_date from date to datetime
            feedback_date = form.cleaned_data['feedback_date']
            if feedback_date:  # Check if it's not None
                feedback_date = datetime.combine(feedback_date, datetime.min.time())  

            # Update the review object manually
            review.feedback_text = form.cleaned_data['feedback_text']
            review.feedback_date = feedback_date  # Assign the converted datetime
            review.feedback_giver = form.cleaned_data['feedback_giver']
            review.save()  # Save changes to Neo4j

            return redirect('feedback_list_neo')

    else:
        form = FeedbackForm(initial={
            'feedback_text': review.feedback_text,
            'feedback_date': review.feedback_date.date() if review.feedback_date else None,  
            'feedback_giver': review.feedback_giver,
        })

    return render(request, 'create_feedback_neo.html', {'form': form, 'title': 'Update Feedback'})



from django.http import Http404

def delete_feedback_neo(request, review_uid):
    material = FeedbackSchema.nodes.get_or_none(uid=review_uid)

    if not material:
        raise Http404("Feedback not found.")

    print(f"Deleting record permanently: {material.uid}")
    material.delete()  # Completely remove from DB
    print("Record deleted successfully.")

    return redirect('feedback_list_neo')

 # Redirect after deletion




from django.shortcuts import render, redirect
from .forms import PurchaseOrderForm
from .models import PurchaseOrder

def create_purchase_order_sqlite(request):
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("purchase_order_sqlite")  # Replace with the actual view name
    else:
        form = PurchaseOrderForm()

    return render(request, "create_purchase_order.html", {"form": form})


def purchase_order_list(request):
    orders = PurchaseOrder.objects.all()
    return render(request, "purchase_order_list.html", {"orders": orders})


from django.shortcuts import render, get_object_or_404, redirect
from .models import PurchaseOrder
from .forms import PurchaseOrderForm

def edit_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("purchase_order_sqlite")  # Redirect to the purchase order list
    else:
        form = PurchaseOrderForm(instance=order)

    return render(request, "edit_purchase_order_sqlite.html", {"form": form, "order": order})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import PurchaseOrder

def delete_purchase_order(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == "POST":
        order.delete()
        messages.success(request, "Purchase order deleted successfully.")
        return redirect("purchase_order_sqlite")  # Redirect to the purchase order list

    return render(request, "delete_purchase_order_sqlite.html", {"order": order})




from django.shortcuts import render, redirect
from .forms import PurchaseOrderForm, BillGenerationForm
from .models import PurchaseOrder, BillGeneration

def create_bill_generation_sqlite(request):
    if request.method == "POST":
        form = BillGenerationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("bill_order_sqlite")  # Replace with the actual view name
    else:
        form = BillGenerationForm()

    return render(request, "create_bill_order_sqlite.html", {"form": form})


def bill_generation_list(request):
    orders = BillGeneration.objects.all()
    return render(request, "bill_order_sqlite.html", {"orders": orders})


def edit_bill_generation(request, pk):
    order = get_object_or_404(BillGeneration, pk=pk)
    
    if request.method == "POST":
        form = BillGenerationForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("bill_order_sqlite")  # Redirect to the purchase order list
    else:
        form = BillGenerationForm(instance=order)

    return render(request, "edit_purchase_order_sqlite.html", {"form": form, "order": order})


from django.contrib import messages


def delete_bill_generation(request, pk):
    order = get_object_or_404(BillGeneration, pk=pk)
    
    if request.method == "POST":
        order.delete()
        messages.success(request, "Bill deleted successfully.")
        return redirect("bill_order_sqlite")  # Redirect to the purchase order list

    return render(request, "delete_bill_order_sqlite.html", {"order": order})
