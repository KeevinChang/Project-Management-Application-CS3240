from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Profile management
    path('account_creation/', views.account_creation, name='account_creation'),
    path('profile/', views.user_profile, name='user_profile'),
    path('update_user_fields/', views.update_user_fields, name='update_user_fields'),
    path('delete_user/', views.delete_user, name='delete_user'),
    # File-related paths
    path('files/', views.file_list, name='file_list'),
    # Authentication paths
    path('logout/', LogoutView.as_view(), name='logout'),
]
