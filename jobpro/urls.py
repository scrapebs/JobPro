from django.urls import include, path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('vacancy/list/', views.vacancies_list, name='vacancies_list'),
	path('vacancy/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
	path('vacancy/new/', views.vacancy_new, name='vacancy_new'),
	path('vacancy/<int:pk>/edit/', views.vacancy_edit, name='vacancy_edit'),
	path('vacancy/<int:pk>/remove/', views.vacancy_remove, name='vacancy_remove'),
	path('vacancy/favourite/change', views.vacancy_favourite_change, name='vacancy_favourite_change'),
	path('vacancy/favourite/list', views.vacancy_favourite_list, name='vacancy_favourite_list'),
	path('vacancy/my/list/', views.my_vacancies_list, name='my_vacancies_list'),
	path('cv/list', views.cv_list, name='cv_list'),
	path('cv/<int:pk>/', views.cv_detail, name='cv_detail'),
	path('cv/new/', views.cv_new, name='cv_new'),
	path('cv/<int:pk>/edit/', views.cv_edit, name='cv_edit'),
	path('cv/<int:pk>/remove/', views.cv_remove, name='cv_remove'),
	path('cv/favourite/change', views.cv_favourite_change, name='cv_favourite_change'),
	path('cv/favourite/list', views.cv_favourite_list, name='cv_favourite_list'),
	path('cv/my', views.cv_my, name='cv_my'),
		
] 
