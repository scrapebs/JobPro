from django.urls import include, path
from . import views

urlpatterns = [
	path('', views.logout, name='my_logout', kwargs={'next_page': '/'}),
] 
