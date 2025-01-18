from django.contrib import admin
from django.urls import path,include
from . import views
from . import marklogic_view

from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)