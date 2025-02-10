from django.contrib import admin
from django.urls import path,include
from . import views
from . import marklogic_view

from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from django.conf import settings
from django.conf.urls.static import static

from .views import create_student_couch, student_list_couch, edit_student_couch, delete_student_couch

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
    path("edit_student_couch/<str:student_id>/", views.edit_student_couch, name="edit_student_couch"),
    path("delete_student_couch/<str:student_id>/", views.delete_student_couch, name="delete_student_couch"),

    path("create_teacher_couch/", views.create_teacher_couch, name="create_teacher_couch"),
    path("teacher_list_couch/", views.teacher_list_couch, name="teacher_list_couch"),
    path("edit_teacher_couch/<str:teacher_id>/", views.edit_teacher_couch, name="edit_teacher_couch"),
    path("delete_teacher_couch/<str:teacher_id>/", views.delete_teacher_couch, name="delete_teacher_couch"),

    path('create_sub_category_couch/', views.create_sub_category_couch, name='create_sub_category_couch'),
    path('sub_category_list_couch/', views.sub_category_list_couch, name='sub_category_list_couch'),
    path('edit_sub_category_couch/<str:sub_category_id>/', views.edit_sub_category_couch, name='edit_sub_category_couch'),
    path('delete_sub_category_couch/<str:sub_category_id>/', views.delete_sub_category_couch, name='delete_sub_category_couch'),

    path('create_book_couch/', views.create_book, name='create_book_couch'),
    path('book_list_couch/', views.book_list_couch, name='book_list_couch'),
    path('edit_book_couch/<str:book_id>/', views.edit_book_couch, name='edit_book_couch'),
    path('delete_book_couch/<str:book_id>/', views.delete_book_couch, name='delete_book_couch'),

    path('create_journal_couch/', views.create_journal_couch, name='create_journal_couch'),
    path('journal_list_couch/', views.journal_list_couch, name='journal_list_couch'),
    path('edit_journal_couch/<str:book_id>/', views.edit_journal_couch, name='edit_journal_couch'),
    path('delete_journal_couch/<str:book_id>/', views.delete_journal_couch, name='delete_journal_couch'),

    path('create_supplier_couch/', views.create_supplier_couch, name='create_supplier_couch'),
    path('supplier_list_couch/', views.supplier_list_couch, name='supplier_list_couch'),
    path('edit_supplier_couch/<str:book_id>/', views.edit_supplier_couch, name='edit_supplier_couch'),
    path('delete_supplier_couch/<str:book_id>/', views.delete_supplier_couch, name='delete_supplier_couch'),

    path('create_material_couch/', views.create_material_couch, name='create_material_couch'),
    path('material_list_couch/', views.material_list_couch, name='material_list_couch'),
    path('edit_material_couch/<str:book_id>/', views.edit_material_couch, name='edit_material_couch'),
    path('delete_material_couch/<str:book_id>/', views.delete_material_couch, name='delete_material_couch'),


    path('teaching_material_list_neo/', views.teaching_material_list_neo, name='teaching_material_list_neo'),
    path('create_teaching_material_neo/', views.create_teaching_material_neo, name='create_teaching_material_neo'),
    path('update_teaching_material_neo/<str:material_id>/', views.update_teaching_material_neo, name='update_teaching_material_neo'),
    path('delete_teaching_material_neo/<str:material_id>/', views.delete_teaching_material_neo, name='delete_teaching_material_neo'),

    path('create_review_neo/', views.create_review_neo, name='create_review_neo'),
    path('review_list_neo/', views.review_list_neo, name='review_list_neo'),
    path('update_review_neo/<str:review_uid>/', views.update_review_neo, name='update_review_neo'),
    path('delete_review_neo/<str:review_uid>/', views.delete_review_neo, name='delete_review_neo'),


    path('create_feedback_neo/', views.create_feedback_neo, name='create_feedback_neo'),
    path('feedback_list_neo/', views.feedback_list_neo, name='feedback_list_neo'),
    path('update_feedback_neo/<str:review_uid>/', views.update_feedback_neo, name='update_feedback_neo'),
    path('delete_feedback_neo/<str:review_uid>/', views.delete_feedback_neo, name='delete_feedback_neo'),

    path('create_purchase_order_list_sqlite/', views.create_purchase_order_sqlite, name='create_purchase_order_sqlite'),
    path("purchase_order_sqlite/", views.purchase_order_list, name="purchase_order_sqlite"),  # Add this line
    path("edit_purchase_order_sqlite/<int:pk>/", views.edit_purchase_order, name="edit_purchase_order_sqlite"),
    path("delete_purchase_order_sqlite/<int:pk>/", views.delete_purchase_order, name="delete_purchase_order_sqlite"),


    path('create_bill_order_sqlite/', views.create_bill_generation_sqlite, name='create_bill_order_sqlite'),
    path("bill_order_sqlite/", views.bill_generation_list, name="bill_order_sqlite"),  # Add this line
    path("edit_bill_order_sqlite/<int:pk>/", views.edit_bill_generation, name="edit_bill_order_sqlite"),
    path("delete_bill_order_sqlite/<int:pk>/", views.delete_bill_generation, name="delete_bill_order_sqlite"),
    
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
