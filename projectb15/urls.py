"""
URL configuration for projectb15 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import CustomLoginView

urlpatterns = [
    path("", views.home, name="home"),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.socialaccount.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', include('users.urls')),  
    path('post_login_redirect/', views.post_login_redirect, name='post_login_redirect'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('events/', views.EventsListView.as_view(), name='events'),
    path('public-events/', views.PublicEventsListView.as_view(), name='public-events'),
    path('events/create/', views.EventCreate.as_view(), name='event-create'),
    path('events/<int:pk>', views.EventDetail.as_view(), name='event-detail'),
    path('events/<int:pk>/update/', views.EventUpdate.as_view(), name='event-update'),
    path('events/<int:pk>/upload/', views.upload_file, name='upload'),
    path('events/<int:pk>/delete/', views.EventDelete.as_view(), name='event-delete'),
    path('events/<int:pk>/upload/', views.upload_file, name='upload_file'),
    path('events/<int:pk>/messages/', views.MessagesListView.as_view(), name='event-messages'),
    path('events/<int:pk>/manage-files/', views.ManageFilesList.as_view(), name='manage-files'),
    path('files/', views.file_list, name='file_list'),
    path('invites/', views.InvitesListView.as_view(), name='invites'),
    path('events-admin/', views.AdminEventList.as_view(), name='admin_events')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)