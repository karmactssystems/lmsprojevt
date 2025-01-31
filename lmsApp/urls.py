from django.contrib import admin
from django.urls import path,include
from . import views
from . import marklogic_view

from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from .views import create_student_couch, student_list_couch

urlpatterns = [
    path('',views.home, name="home-page"),
    path('login',views.login_page,name='login-page'),
    path('register',views.userregister,name='register-page'),
    path('save_register',views.save_register,name='register-user'),
    path('user_login',views.login_user,name='login-user'),
    path('home',views.home,name='home-page'),
    path('logout',views.logout_user,name='logout'),
    path('profile',views.profile,name='profile-page'),
    path('update_password',views.update_password,name='update-password'),
    path('update_profile',views.update_profile,name='update-profile'),
    path('users',views.users,name='user-page'),
    path('manage_user',views.manage_user,name='manage-user'),
    path('manage_user/<int:pk>',views.manage_user,name='manage-user-pk'),
    path('save_user',views.save_user,name='save-user'),
    path('delete_user/<int:pk>',views.delete_user,name='delete-user'),
    path('category',views.category,name='category-page'),
    path('manage_category',views.manage_category,name='manage-category'),
    path('manage_category/<int:pk>',views.manage_category,name='manage-category-pk'),
    path('view_category/<int:pk>',views.view_category,name='view-category-pk'),
    path('save_category',views.save_category,name='save-category'),
    path('delete_category/<str:pk>',views.delete_category,name='delete-category'),
    path('sub_category',views.sub_category,name='sub_category-page'),
    path('supplier',views.supplier_list,name='supplier'),
    
    path('manage_sub_category',views.manage_sub_category,name='manage-sub_category'),
    path('manage_supplier',views.manage_supplier,name='manage_supplier'),
    path('manage_supplier/<int:pk>',views.manage_supplier,name='manage-supplier-pk'),
    

    path('manage_sub_category/<int:pk>',views.manage_sub_category,name='manage-sub_category-pk'),
    path('view_sub_category/<int:pk>',views.view_sub_category,name='view-sub_category-pk'),
    path('save_sub_category',views.save_sub_category,name='save-sub_category'),
    path('save_sub_supplier',views.save_supplier,name='save_sub_supplier'),
    
    path('delete_sub_category/<int:pk>',views.delete_sub_category,name='delete-sub_category'),
    path('books',views.books,name='book-page'),
    path('manage_book',views.manage_book,name='manage-book'),
    path('manage_book/<int:pk>',views.manage_book,name='manage-book-pk'),
    path('view_book/<int:pk>',views.view_book,name='view-book-pk'),
    path('save_book',views.save_book,name='save-book'),
    path('delete_book/<int:pk>',views.delete_book,name='delete-book'),
    path('students',views.students,name='student-page'),
    path('manage_student',views.manage_student,name='manage-student'),
    path('manage_student/<int:pk>',views.manage_student,name='manage-student-pk'),
    path('view_student/<int:pk>',views.view_student,name='view-student-pk'),
    path('save_student',views.save_student,name='save-student'),
    path('delete_student/<int:pk>',views.delete_student,name='delete-student'),


    path('get_borrows',views.get_borrows,name='borrow-page'),
    path('manage_borrow',views.manage_borrow,name='manage-borrow'),
    path('manage_borrow/<int:pk>',views.manage_borrow,name='manage-borrow-pk'),
    path('view_borrow/<int:pk>',views.view_borrow,name='view-borrow-pk'),
    path('save_borrow',views.save_borrow,name='save-borrow'),
    path('delete_borrow/<int:pk>',views.delete_borrow,name='delete-borrow'),


    path('create_student/', marklogic_view.create_student_view, name='create_student'),
    path('list_students/', marklogic_view.list_students_view, name='list_students'),
    path('insert_dummy/', views.insert_dummy_data, name='insert_dummy'),
    path('create_collection/', views.create_arango_collections, name='create_collection'),


    path('save_teaching_material/', views.save_teaching_material, name='save-teaching-material'),
    path('get_teaching_material/', views.get_teaching_materials, name='teaching-material-page'),
    path('manage_teaching_material/', views.manage_teaching_material, name='manage-teaching-material'),
    path('manage_teaching_material/<int:pk>/', views.manage_teaching_material, name='manage-teaching-material-pk'),
    path('view_teaching_material/<int:pk>/', views.view_teaching_material, name='view-teaching-material'),
    path('delete_teaching_material/<int:pk>/', views.delete_teaching_material, name='delete-teaching-material'),
    path('download_file/<str:file_key>/', views.download_file, name='download-file'),
    
    path('save_user_info/', views.save_user_info, name='save-user-info'),
    path('get_user_info/', views.get_user_info, name='user-info-page'),
    path('manage_user_info',views.manage_user_info,name='manage-user-info'),
    path('manage_user_info/<int:pk>',views.manage_user_info,name='manage-user-info-pk'),
    path('view_user_info/<int:pk>',views.view_user_info,name='view-user-info'),
    path('delete_user_info/<int:pk>/', views.delete_user_info, name='delete-user-info'),


    path("create_student_couch/", create_student_couch, name="create_student_couch"),
    path("students_list_couch/", student_list_couch, name="student_list_couch"),
    
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
