from django.conf.urls import url
from django.urls import include, path
from . import views

urlpatterns = [
	#path('reg', views.update_profile, name='update_profile'),
	path('', views.index, name='index'),
	url(r'^vacancy/list/$', views.vacancies_list, name='vacancies_list'),
	url(r'^vacancy/(?P<pk>\d+)/$', views.vacancy_detail, name='vacancy_detail'),
	url(r'^vacancy/new/$', views.vacancy_new, name='vacancy_new'),
	url(r'^vacancy/(?P<pk>\d+)/edit/$', views.vacancy_edit, name='vacancy_edit'),
	path('vacancy/<int:pk>/remove/', views.vacancy_remove, name='vacancy_remove'),
	url(r'^favourite/change$', views.vacancy_favourite_change, name='vacancy_favourite_change'),
	url(r'^favourite/list$', views.favourite_list, name='favourite_list'),
	path('vacancy/my/list/', views.my_vacancies_list, name='my_vacancies_list'),
	
	
] 

#urlpatterns = []