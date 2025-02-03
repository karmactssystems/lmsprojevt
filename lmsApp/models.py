from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from PIL import Image
from django.contrib.auth.models import User
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from datetime import datetime

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null= True)
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Categories"

    def __str__(self):
        return str(f"{self.name}")


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete= models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null= True)
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Categories"

    def __str__(self):
        return str(f"{self.category} - {self.name}")

class Books(models.Model):
    sub_category = models.CharField(max_length=250)
    isbn = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null= True)
    author = models.TextField(blank=True, null= True)
    publisher = models.CharField(max_length=250)
    date_published = models.DateTimeField()
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Books"

    def __str__(self):
        return str(f"{self.isbn} - {self.title}")


class Students(models.Model):
    code = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    middle_name = models.CharField(max_length=250, blank=True, null= True)
    last_name = models.CharField(max_length=250)
    gender = models.CharField(max_length=20, choices=(('Male','Male'), ('Female','Female')), default = 'Male')
    contact = models.CharField(max_length=250)
    email = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    department = models.CharField(max_length=250, blank= True, null = True)
    course = models.CharField(max_length=250, blank= True, null = True)
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)
    date_added = models.DateTimeField(default = timezone.now)
    date_created = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name_plural = "List of Students"

    def __str__(self):
        return str(f"{self.code} - {self.first_name}{' '+self.middle_name if not self.middle_name == '' else ''} {self.last_name}")

    def name(self):
        return str(f"{self.first_name}{' '+self.middle_name if not self.middle_name == '' else ''} {self.last_name}")


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()


class TeachingMaterial(models.Model):
    name = models.CharField(max_length=250, blank=True, null= True)
    subject = models.CharField(max_length=250, blank=True, null= True)
    course = models.CharField(max_length=250, blank=True, null= True)
    teaching_reference = models.FileField(upload_to='teaching_materials/', null=True, blank=True)
    delete_flag = models.IntegerField(default = 0)

    class Meta:
        verbose_name_plural = "Teaching Materials"

    def __str__(self):
        return str(f"{self.name} {self.subject} {self.course} {self.teaching_reference}") 
    

class UserInfo(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    membership_type = models.CharField(max_length=4, choices=(('1','Student'), ('2','Adult'), ('3','Senior'), ('4','Teacher')), default = 1)
    join_date = models.DateField()
    status = models.CharField(max_length=2, choices=(('1','Active'), ('2','Inactive')), default = 1)
    delete_flag = models.IntegerField(default = 0)

    class Meta:
        verbose_name = "User Information"
        verbose_name_plural = "User Information"

    def __str__(self):
        return self.name
    

class Borrow(models.Model):
    # student = models.ForeignKey(Students, on_delete= models.CASCADE, related_name="student_id_fk")
    book = models.CharField(max_length=250, blank=True, null= True)
    borrowing_date = models.DateField()
    return_date = models.DateField()
    status = models.CharField(max_length=2, choices=(('1','Pending'), ('2','Returned')), default = 1)
    date_added = models.DateTimeField(default = timezone.now)
    date_created = models.DateTimeField(auto_now = True)
    due_date = models.DateField(default = timezone.now)
    fines = models.IntegerField(default=0)
    user = models.CharField(max_length=250, blank=True, null= True)
    delete_flag = models.IntegerField(default = 0)

    class Meta:
        verbose_name_plural = "Borrowing Transactions"

    def __str__(self):
        return self.book
    


# Create your models here.
from neomodel import StructuredNode, StringProperty, IntegerProperty,UniqueIdProperty, RelationshipTo, DateTimeProperty
#neo4j models
class City(StructuredNode):
    code = StringProperty(unique_index=True, required=True)
    name = StringProperty(index=True, default="city")

class Person(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True)
    age = IntegerProperty(index=True, default=0)

    # Relations :
    city = RelationshipTo(City, 'LIVES_IN')
    friends = RelationshipTo('Person','FRIEND')

class StudentSchema(StructuredNode):
    code = StringProperty(unique_index=True, required=True)
    first_name = StringProperty(index=True)
    middle_name = StringProperty(index=True, required=False)
    last_name = StringProperty(index=True)
    gender = StringProperty(index=True, choices={"Male": "Male", "Female": "Female"}, default="Male")
    contact = StringProperty(index=True)
    email = StringProperty(index=True)
    address = StringProperty(index=True)
    department = StringProperty(index=True, required=False)
    course = StringProperty(index=True, required=False)
    status = StringProperty(index=True, choices={"1": "Active", "2": "Inactive"}, default="1")
    delete_flag = IntegerProperty(default=0)
    date_added = StringProperty(default=datetime.now().isoformat, index=True)
    date_created = StringProperty(default=datetime.now().isoformat, index=True)

    def name(self):
        return f"{self.first_name} {' ' + self.middle_name if self.middle_name else ''} {self.last_name}"



#teaching material, review and feedback model for neo
class TeachingMaterialSchema(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(index=True, required=False)
    subject = StringProperty(index=True, required=False)
    course = StringProperty(index=True, required=False)
    teaching_reference = StringProperty(index=True, required=False)
    delete_flag = IntegerProperty(default=0)

    def __str__(self):
        return f"{self.name or ''} {self.subject or ''} {self.course or ''} {self.teaching_reference or ''}"
    

class Review(StructuredNode):
    review_text = StringProperty(required=True)
    rating = IntegerProperty(min=1, max=5, required=True)  # Rating between 1 to 5
    review_date = DateTimeProperty(default=datetime.now)  # Automatically set the review date
    reviewer_name = StringProperty(required=True)

    # Relationship to TeachingMaterialSchema
    reviewed_material = RelationshipTo('TeachingMaterialSchema', 'REVIEWS')

    def __str__(self):
        return f"Review by {self.reviewer_name} for {self.reviewed_material.name}: {self.rating} stars"
    
class Feedback(StructuredNode):
    feedback_text = StringProperty(required=True)
    feedback_date = DateTimeProperty(default=datetime.now)  # Automatically set the feedback date
    feedback_giver = StringProperty(required=True)

    # Relationship to Review
    feedback_for_review = RelationshipTo('Review', 'GIVES_FEEDBACK')

    def __str__(self):
        return f"Feedback by {self.feedback_giver}: {self.feedback_text}"
