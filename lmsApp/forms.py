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
    teaching_reference = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

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
        fields = ('name', 'address', 'phone_number', 'email', 'membership_type', 'join_date', 'status')

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
    borrowing_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    return_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    status = forms.CharField(max_length=2)
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fines = forms.IntegerField()
    user = forms.ChoiceField()  # This will be populated with UserInfo data

    class Meta:
        model = models.Borrow
        fields = ('book', 'borrowing_date', 'return_date', 'status', 'due_date', 'fines', 'user')

    def __init__(self, *args, **kwargs):
        super(SaveBorrow, self).__init__(*args, **kwargs)
        # Populate the user field with choices from the UserInfo collection in ArangoDB
        users = [(user.id, user.username) for user in models.UserInfo.objects.all()]  # Assuming Django ORM mapping
        self.fields['user'].choices = users

    def clean_user(self):
        user = int(self.data['user']) if (self.data['user']).isnumeric() else 0
        try:
            user = models.UserInfo.objects.get(id=user)
            return user
        except models.UserInfo.DoesNotExist:
            raise forms.ValidationError("Invalid user.")

    def clean_book(self):
        book = int(self.data['book']) if (self.data['book']).isnumeric() else 0
        try:
            book = models.Books.objects.get(id=book)
            return book
        except models.Books.DoesNotExist:
            raise forms.ValidationError("Invalid Book.")
