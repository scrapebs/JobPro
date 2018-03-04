from django.contrib import admin
from django.conf.urls import include, url
from django.urls import path
from django.contrib.auth import views

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('accounts/login/', views.login, name='login'),
    path('accounts/logout/', include('myauth.urls')),
    path('', include('jobpro.urls')),
    path('accounts/', include('myregistration.backends.simple.urls')),
]