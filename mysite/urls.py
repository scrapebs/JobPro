from django.contrib import admin
from django.conf.urls import include, url
from django.urls import path
from django.contrib.auth import views

urlpatterns = [
    url('admin/', admin.site.urls),    
    url(r'^accounts/login/$', views.login, name='login'),
    #url(r'^accounts/logout/$', views.logout, name='logout', kwargs={'next_page': '/'}),
    path('accounts/logout/', include('myauth.urls')),
    url(r'', include('jobpro.urls')),
    url(r'^accounts/', include('myregistration.backends.simple.urls')),
]