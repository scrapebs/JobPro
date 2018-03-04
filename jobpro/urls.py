from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vacancy/list/', views.vacancies_list, name='vacancies_list'),
    path('vacancy/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancy/new/', views.vacancy_new, name='vacancy_new'),
    path('vacancy/<int:pk>/edit/', views.vacancy_edit, name='vacancy_edit'),
    path('vacancy/<int:pk>/remove/', views.vacancy_remove, name='vacancy_remove'),
    path('vacancy/favourite/change/', views.vacancy_favourite_change, name='vacancy_favourite_change'),
    path('vacancy/favourite/list/', views.vacancy_favourite_list, name='vacancy_favourite_list'),
    path('favourite/general/', views.favourite_general, name='favourite_general'),
    path('vacancy/my/list/', views.my_vacancies_list, name='my_vacancies_list'),
    path('cv/list/', views.cv_list, name='cv_list'),
    #path('cv/list/', views.CvView.as_view(), name='cv_list'),  #generic
    path('cv/<int:pk>/', views.cv_detail, name='cv_detail'),
    path('cv/new/', views.cv_new, name='cv_new'),
    path('cv/<int:pk>/edit/', views.cv_edit, name='cv_edit'),
    path('cv/<int:pk>/remove/', views.cv_remove, name='cv_remove'),
    path('cv/favourite/change/', views.cv_favourite_change, name='cv_favourite_change'),
    path('cv/favourite/list/', views.cv_favourite_list, name='cv_favourite_list'),
    path('cv/my/', views.cv_my, name='cv_my'),
    path('organisation/<int:pk>/', views.org_info_detail, name='org_info_detail'),    
    path('organisation/my/', views.org_info_my, name='org_info_my'),
    path('organisation/new/', views.org_info_new, name='org_info_new'),
    path('organisation/<int:pk>/edit/', views.org_info_edit, name='org_info_edit'),
    path('organisation/<int:pk>/remove/', views.org_info_remove, name='org_info_remove'),
    path('organisation/owner/<int:owner_pk>/', views.org_info_vacancy, name='org_info_vacancy'),
    path('organisation/<int:pk>/vacancy/list/', views.org_vacancies_list, name='org_vacancies_list'),
] 


