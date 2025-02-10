from datetime import datetime
from random import random
from secrets import choice
from sys import prefix
from unicodedata import category
from django import forms
from numpy import require
from lmsApp import models

from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User
import datetime

class SaveUser(UserCreationForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    password1 = forms.CharField(max_length=250)
    password2 = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name','password1', 'password2',)

class UpdateProfile(UserChangeForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name')

    def clean_current_password(self):
        if not self.instance.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(f"Password is Incorrect")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")

class UpdateUser(UserChangeForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")

class UpdatePasswords(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Old Password")
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="New Password")
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Confirm New Password")
    class Meta:
        model = User
        fields = ('old_password','new_password1', 'new_password2')

class SaveCategory(forms.ModelForm):
    name = forms.CharField(max_length=250)
    description = forms.Textarea()
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Category
        fields = ('name', 'description', 'status', )

    def clean_name(self):
        id = self.data['id'] if (self.data['id']).isnumeric() else 0
        name = self.cleaned_data['name']
        try:
            if id > 0:
                category = models.Category.objects.exclude(id = id).get(name = name, delete_flag = 0)
            else:
                category = models.Category.objects.get(name = name, delete_flag = 0)
        except:
            return name
        raise forms.ValidationError("Category Name already exists.")

class SaveSubCategory(forms.ModelForm):
    category = forms.CharField(max_length=250)
    name = forms.CharField(max_length=250)
    description = forms.Textarea()
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.SubCategory
        fields = ('category', 'name', 'description', 'status', )

    def clean_category(self):
        cid = int(self.data['category']) if (self.data['category']).isnumeric() else 0
        try:
            category = models.Category.objects.get(id = cid)
            return category
        except:
            raise forms.ValidationError("Invalid Category.")

    def clean_name(self):
        id = int(self.data['id']) if (self.data['id']).isnumeric() else 0
        cid = int(self.data['category']) if (self.data['category']).isnumeric() else 0
        name = self.cleaned_data['name']
        try:
            category = models.Category.objects.get(id = cid)
            if id > 0:
                sub_category = models.SubCategory.objects.exclude(id = id).get(name = name, delete_flag = 0, category = category)
            else:
                sub_category = models.SubCategory.objects.get(name = name, delete_flag = 0, category = category)
        except:
            return name
        raise forms.ValidationError("Sub-Category Name already exists on the selected Category.")
     
class SaveBook(forms.ModelForm):
    sub_category = forms.CharField(max_length=250)
    isbn = forms.CharField(max_length=250)
    title = forms.CharField(max_length=250)
    description = forms.Textarea()
    author = forms.Textarea()
    publisher = forms.Textarea()
    date_published = forms.DateField()
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Books
        fields = ('isbn', 'sub_category', 'title', 'description', 'author', 'publisher', 'date_published', 'status', )

    # def clean_sub_category(self):
    #     scid = int(self.data['sub_category']) if (self.data['sub_category']).isnumeric() else 0
    #     try:
    #         sub_category = models.SubCategory.objects.get(id = scid)
    #         return sub_category
    #     except:
    #         raise forms.ValidationError("Invalid Sub Category.")

    def clean_isbn(self):
        id = int(self.data['id']) if (self.data['id']).isnumeric() else 0
        isbn = self.cleaned_data['isbn']
        try:
            if id > 0:
                book = models.Books.objects.exclude(id = id).get(isbn = isbn, delete_flag = 0)
            else:
                book = models.Books.objects.get(isbn = isbn, delete_flag = 0)
        except:
            return isbn
        raise forms.ValidationError("ISBN already exists on the Database.")

class SaveSupplier(forms.Form):
    name=forms.CharField(max_length=250)
    office_address=forms.CharField(max_length=250)
    mobile_no=forms.CharField(max_length=250)
    email_id=forms.CharField(max_length=250)
class SaveStudent(forms.ModelForm):
    code = forms.CharField(max_length=250)
    first_name = forms.CharField(max_length=250)
    middle_name = forms.CharField(max_length=250, required= False)
    last_name = forms.CharField(max_length=250)
    gender = forms.CharField(max_length=250)
    contact = forms.CharField(max_length=250)
    email = forms.CharField(max_length=250)
    department = forms.CharField(max_length=250)
    course = forms.CharField(max_length=250)
    address = forms.Textarea()
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Students
        fields = ('code', 'first_name', 'middle_name', 'last_name', 'gender', 'contact', 'email', 'address', 'department', 'course', 'status', )

    def clean_code(self):
        id = int(self.data['id']) if (self.data['id']).isnumeric() else 0
        code = self.cleaned_data['code']
        try:
            if id > 0:
                book = models.Books.objects.exclude(id = id).get(code = code, delete_flag = 0)
            else:
                book = models.Books.objects.get(code = code, delete_flag = 0)
        except:
            return code
        raise forms.ValidationError("Student School Id already exists on the Database.")
    
    
class UserForm(forms.Form):
    code = forms.CharField(max_length=250)
    first_name = forms.CharField(max_length=250)
    middle_name = forms.CharField(max_length=250, required= False)
    last_name = forms.CharField(max_length=250)
    gender = forms.CharField(max_length=250)
    contact = forms.CharField(max_length=250)
    email = forms.CharField(max_length=250)
    department = forms.CharField(max_length=250)
    course = forms.CharField(max_length=250)
    address = forms.Textarea()
    status = forms.CharField(max_length=2)
    user_type= forms.CharField(max_length=15)
    created_at = forms.DateTimeField(required=False)
    class Meta:
        model = models.Students
        fields = ('code', 'first_name', 'middle_name', 'last_name', 'gender', 'contact', 'email', 'address', 'department', 'course', 'status', )
    def clean_created_at(self):
        created_at = datetime.datetime.now()
        return created_at



class SaveTeachingMaterial(forms.ModelForm):
    name = forms.CharField(max_length=250)
    subject = forms.CharField(max_length=250)
    course = forms.CharField(max_length=250)
    teaching_reference = forms.FileField()

    class Meta:
        model = models.TeachingMaterial
        fields = ('name', 'subject', 'course', 'teaching_reference',)

    def clean_name(self):
        name = self.cleaned_data['name']
        
        # Safely get the ID, defaulting to 0 if it's empty or not provided
        id_value = self.data.get('id', 0)
        try:
            id = int(id_value) if id_value else 0  # Handle empty string or missing value
        except ValueError:
            raise forms.ValidationError("Invalid ID value.")

        # Now perform the duplicate check
        try:
            if id > 0:
                material = models.TeachingMaterial.objects.exclude(id=id).get(name=name, delete_flag=False)
            else:
                material = models.TeachingMaterial.objects.get(name=name, delete_flag=False)
        except models.TeachingMaterial.DoesNotExist:
            return name  # If no duplicate is found, return the name
        
        # Raise validation error if a duplicate is found
        raise forms.ValidationError("Teaching Material name already exists in the database.")
    
    def clean_subject(self):
        subject = self.cleaned_data['subject']
        return subject
    
    def clean_course(self):
        course = self.cleaned_data['course']
        return course
    
    def clean_teaching_reference(self):
        teaching_reference = self.cleaned_data['teaching_reference']
        return teaching_reference

class SaveUserInfo(forms.ModelForm):
    name = forms.CharField(max_length=255)
    address = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=15)
    email = forms.EmailField()
    membership_type = forms.CharField(max_length=3)
    join_date = forms.DateField()
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.UserInfo
        fields = ('name', 'address', 'phone_number', 'email', 'membership_type', 'join_date', 'status', )

    def clean_name(self):
        name = self.cleaned_data['name']
        
        # Safely convert id to an integer, defaulting to 0 if it's not provided or is empty
        try:
            id = int(self.data.get('id', 0) or 0)
        except ValueError:
            id = 0
    
        try:
            if id > 0:
                material = models.UserInfo.objects.exclude(id=id).get(name=name, delete_flag=False)
            else:
                material = models.UserInfo.objects.get(name=name, delete_flag=False)
        except models.UserInfo.DoesNotExist:
            return name
        
        raise forms.ValidationError("User Info name already exists in the database.")


class SaveBorrow(forms.ModelForm):
    book = forms.CharField(max_length=250)
    borrowing_date = forms.DateField()
    return_date = forms.DateField()
    status = forms.CharField(max_length=2)
    due_date = forms.DateField()
    fines = forms.IntegerField()
    user = forms.CharField(max_length=250)

    class Meta:
        model = models.Borrow
        fields = ('book', 'borrowing_date', 'return_date', 'status', 'due_date', 'fines', 'user')

    def clean_book(self):
        book = self.cleaned_data['book']
        
        # Safely convert id to an integer, defaulting to 0 if it's not provided or is empty
        try:
            id = int(self.data.get('id', 0) or 0)
        except ValueError:
            id = 0
    
        try:
            if id > 0:
                material = models.Borrow.objects.exclude(id=id).get(book=book, delete_flag=False)
            else:
                material = models.Borrow.objects.get(book=book, delete_flag=False)
        except models.Borrow.DoesNotExist:
            return book
        
        raise forms.ValidationError("Borrow Transaction already exists in the database.")
            


class StudentForm(forms.Form):
    code = forms.CharField(max_length=250)
    first_name = forms.CharField(max_length=250)
    middle_name = forms.CharField(max_length=250, required=False)
    last_name = forms.CharField(max_length=250)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')], initial='Male')
    contact = forms.CharField(max_length=250)
    email = forms.EmailField(max_length=250)
    address = forms.CharField(max_length=250)
    department = forms.CharField(max_length=250, required=False)
    course = forms.CharField(max_length=250, required=False)
    status = forms.ChoiceField(choices=[('1', 'Active'), ('2', 'Inactive')], initial='1')

from django.utils import timezone

class SaveReview(forms.ModelForm):
    book_assigned = forms.CharField(max_length=255)
    review_text = forms.CharField(widget=forms.Textarea)
    rating = forms.IntegerField(min_value=1, max_value=5)
    review_date = forms.DateTimeField(initial=timezone.now, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    reviewer_name = forms.CharField(max_length=250)

    class Meta:
        model = models.ReviewModel
        fields = ('book_assigned', 'review_text', 'rating', 'review_date', 'reviewer_name')

    def clean_book(self):
        book = self.cleaned_data['book_assigned']
        return book
    
    def clean_review_text(self):
        review_text = self.cleaned_data['review_text']
        return review_text
    
class SaveFeedback(forms.ModelForm):
    teaching_assigned = forms.CharField(max_length=255)
    feedback_text = forms.CharField(widget=forms.Textarea)
    feedback_date = forms.DateTimeField(initial=timezone.now, widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    feedback_giver = forms.CharField(max_length=250)

    class Meta:
        model = models.FeedbackModel
        fields = ('teaching_assigned', 'feedback_text', 'feedback_date', 'feedback_giver')

    def clean_teaching_assigned(self):
        teaching_assigned = self.cleaned_data['teaching_assigned']
        return teaching_assigned
    
    def clean_feedback_text(self):
        feedback_text = self.cleaned_data['feedback_text']
        return feedback_text


class TeacherForm(forms.Form):
    first_name = forms.CharField(max_length=250)
    middle_name = forms.CharField(max_length=250, required=False)
    last_name = forms.CharField(max_length=250)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')], initial='Male')
    contact = forms.CharField(max_length=250)
    email = forms.EmailField(max_length=250)
    address = forms.CharField(max_length=250)
    department = forms.CharField(max_length=250, required=False)
    course = forms.CharField(max_length=250, required=False)
    status = forms.ChoiceField(choices=[('1', 'Active'), ('2', 'Inactive')], initial='1')


class SubCategoryForm(forms.Form):
    name = forms.CharField(max_length=250)
    description = forms.CharField(max_length=250)
    status = forms.ChoiceField(choices=[('1', 'Active'), ('2', 'Inactive')], initial='1')

from django.conf import settings
import couchdb

from django import forms
from django.conf import settings
import couchdb

from django import forms
from django.conf import settings
import couchdb

from django import forms
from django.conf import settings
import couchdb

class BooksForm(forms.Form):
    isbn = forms.CharField(max_length=13, label="ISBN", required=True)
    title = forms.CharField(max_length=250, label="Title", required=True)
    description = forms.CharField(max_length=500, label="Description", widget=forms.Textarea, required=False)
    author = forms.CharField(max_length=250, label="Author", required=True)
    publisher = forms.CharField(max_length=250, label="Publisher", required=True)
    status = forms.ChoiceField(choices=[('1', 'Active'), ('2', 'Inactive')], initial='1', label="Status")

    # Initialize sub_category_choices dynamically in the form's __init__ method
    def __init__(self, *args, **kwargs):
        super(BooksForm, self).__init__(*args, **kwargs)

        # Fetch subcategories from CouchDB
        COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE3['USER']}:{settings.COUCHDB_DATABASE3['PASSWORD']}@127.0.0.1:5984/"
        server = couchdb.Server(COUCHDB_URL)
        db_name = settings.COUCHDB_DATABASE3["NAME"]

        try:
            if db_name in server:
                db = server[db_name]
            else:
                db = server.create(db_name)

            # Retrieve all subcategories from the CouchDB database
            sub_category_choices = []
            for doc_id in db:
                doc = db[doc_id]
                # Check if the document is a sub-category (based on the presence of 'name' field)
                if 'name' in doc:
                    sub_category_name = doc.get('name', 'No Name Found')
                    sub_category_choices.append((doc_id, sub_category_name))

            # In case there are no subcategories, default to an empty choice
            if not sub_category_choices:
                sub_category_choices = [('0', 'No Subcategories Found')]

            # Log the subcategory choices to the console
            print("Subcategory Choices:", sub_category_choices)

        except Exception as e:
            # Handle any CouchDB connection errors
            sub_category_choices = [('0', f'Error fetching subcategories: {str(e)}')]
            print("Error fetching subcategories:", str(e))

        # Dynamically update the sub_category field with the retrieved choices
        self.fields['sub_category'] = forms.ChoiceField(choices=sub_category_choices, label="Sub Category", required=True)


class JournalForm(forms.Form):
    title = forms.CharField(max_length=250, label="Title", required=True)
    description = forms.CharField(max_length=500, label="Description", widget=forms.Textarea, required=False)
    author = forms.CharField(max_length=250, label="Author", required=True)
    publisher = forms.CharField(max_length=250, label="Publisher", required=True)
    status = forms.ChoiceField(choices=[('1', 'Active'), ('2', 'Inactive')], initial='1', label="Status")

    # Initialize sub_category_choices dynamically in the form's __init__ method
    def __init__(self, *args, **kwargs):
        super(JournalForm, self).__init__(*args, **kwargs)

        # Fetch subcategories from CouchDB
        COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE3['USER']}:{settings.COUCHDB_DATABASE3['PASSWORD']}@127.0.0.1:5984/"
        server = couchdb.Server(COUCHDB_URL)
        db_name = settings.COUCHDB_DATABASE3["NAME"]

        try:
            if db_name in server:
                db = server[db_name]
            else:
                db = server.create(db_name)

            # Retrieve all subcategories from the CouchDB database
            sub_category_choices = []
            for doc_id in db:
                doc = db[doc_id]
                # Check if the document is a sub-category (based on the presence of 'name' field)
                if 'name' in doc:
                    sub_category_name = doc.get('name', 'No Name Found')
                    sub_category_choices.append((doc_id, sub_category_name))

            # In case there are no subcategories, default to an empty choice
            if not sub_category_choices:
                sub_category_choices = [('0', 'No Subcategories Found')]

            # Log the subcategory choices to the console
            print("Subcategory Choices:", sub_category_choices)

        except Exception as e:
            # Handle any CouchDB connection errors
            sub_category_choices = [('0', f'Error fetching subcategories: {str(e)}')]
            print("Error fetching subcategories:", str(e))

        # Dynamically update the sub_category field with the retrieved choices
        self.fields['sub_category'] = forms.ChoiceField(choices=sub_category_choices, label="Sub Category", required=True)



class SupplierForm(forms.Form):
    name = forms.CharField(max_length=250, label="Supplier Name", required=True)
    email = forms.EmailField(label="Email Address", required=True)
    phone = forms.CharField(max_length=20, label="Phone Number", required=True)
    address = forms.CharField(widget=forms.Textarea, label="Address", required=True)
    status = forms.ChoiceField(choices=[('1', 'Active'), ('0', 'Inactive')], label="Status", initial='1')



class TeachingMaterialForm(forms.Form):
    name = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    course = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    teaching_reference = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


# forms.py

# class ReviewForm(forms.Form):
#     review_text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=True)
#     rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'class': 'form-control'}), required=True)
#     reviewer_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
#     reviewed_material = forms.CharField(widget=forms.HiddenInput(), required=True)  # Hidden field for material UID

class ReviewForm(forms.Form):
    review_text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=True)
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'class': 'form-control'}), required=True)
    reviewer_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)

    # Dropdown for Teaching Materials
    reviewed_material = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}), required=True)

    def __init__(self, *args, **kwargs):
        materials = kwargs.pop('materials', [])  # Fetch materials passed from the view
        super().__init__(*args, **kwargs)
        self.fields['reviewed_material'].choices = [(m['id'], m['name']) for m in materials]

        print("Dropdown Choices Set:", self.fields['reviewed_material'].choices)  # Debugging Output

class FeedbackForm(forms.Form):
    feedback_text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=True)
    feedback_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),  # 'type': 'date' enables the date picker
        required=False
    )
    feedback_giver = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)


from django import forms
from .models import PurchaseOrder, BillGeneration
import couchdb
from django.conf import settings

class PurchaseOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)

        # Fetch books from CouchDB
        COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE4['USER']}:{settings.COUCHDB_DATABASE4['PASSWORD']}@127.0.0.1:5984/"
        server = couchdb.Server(COUCHDB_URL)

        db_name = settings.COUCHDB_DATABASE4["NAME"]
        if db_name in server:
            db = server[db_name]
            book_choices = [(book_doc.get("title", ""), book_doc.get("title", "")) for doc_id in db for book_doc in [db[doc_id]]]
        else:
            book_choices = []

        book_choices.insert(0, ("", "Select a Book"))  # Add a placeholder

        self.fields['book_name'].widget = forms.Select(choices=book_choices)

    class Meta:
        model = PurchaseOrder
        fields = ['order_number', 'order_date', 'status', 'book_name']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=PurchaseOrder._meta.get_field('status').choices),
        }


class BillGenerationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BillGenerationForm, self).__init__(*args, **kwargs)

        # Fetch books from CouchDB
        COUCHDB_URL = f"http://{settings.COUCHDB_DATABASE6['USER']}:{settings.COUCHDB_DATABASE6['PASSWORD']}@127.0.0.1:5984/"
        server = couchdb.Server(COUCHDB_URL)

        db_name = settings.COUCHDB_DATABASE6["NAME"]
        if db_name in server:
            db = server[db_name]
            book_choices = [(book_doc.get("name", ""), book_doc.get("name", "")) for doc_id in db for book_doc in [db[doc_id]]]
            print("Book choices:", book_choices)
        else:
            book_choices = []

        book_choices.insert(0, ("", "Select a Supplier"))  # Add a placeholder

        self.fields['supplier_name'].widget = forms.Select(choices=book_choices)

    class Meta:
        model = BillGeneration
        fields = ['bill_number', 'bill_date', 'status', 'supplier_name']
        widgets = {
            'bill_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=BillGeneration._meta.get_field('status').choices),
        }
