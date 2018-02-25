from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils import timezone
from .models import User, Vacancy, Cv, Favourite_vacancy, Favourite_cv  
from .forms import VacancyForm, CvForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction 
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
#from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def is_organisation(user):
	if user.is_authenticated: 
		return user.account_type == 'OR'
	else:
		return False

def is_employee(user):
	if user.is_authenticated: 
		return user.account_type == 'EM'
	else:
		return False

def index(request):
	if request.user.is_authenticated == True: 
		return render(request, 'jobpro/index.html', {}, )
	else:
		return render(request, 'jobpro/index_logout.html', {}, )

#список вакансий
def vacancies_list(request):
	vacancies = Vacancy.objects.filter(actual=True).order_by('name')
	is_organisation = False
	favourite_vacancies = None
	if request.user.is_authenticated:
		if request.user.account_type=='OR':
			is_organisation = True
		else:
			favourite_vacancies = Favourite_vacancy.objects.filter(user = request.user)
	return render(request, 'jobpro/vacancies_list.html', {'vacancies':vacancies, 'is_organisation': is_organisation, 'favourite_vacancies': favourite_vacancies}, )


#информация по выбранной вакансии
def vacancy_detail(request, pk):
	vacancy = get_object_or_404(Vacancy, pk=pk)
	#убрать для организации
	is_owner = False
	is_favourite = False
	is_organisation = False
	if request.user.is_authenticated:
		#is_organisation = User.objects.filter(username = request.user, account_type='OR').exists()
		if request.user.account_type=='OR':
			is_organisation = True
			if vacancy.owner == User.objects.get(username = request.user):
				is_owner = True 
		else:
			is_favourite = Favourite_vacancy.objects.filter(user=request.user, vacancy=vacancy).exists()			
	return render(request, 'jobpro/vacancy_detail.html', {'vacancy': vacancy, 'is_organisation': is_organisation, 'is_favourite': is_favourite, 'is_owner': is_owner})


#заведение новой вакансии
@user_passes_test(is_organisation)
def vacancy_new(request):
	if request.method == "POST":
		form = VacancyForm(request.POST)
		if form.is_valid():
			vacancy = form.save(commit=False)
			vacancy.owner = request.user
			vacancy.created_date =  timezone.now()
			vacancy.save()
			return redirect('vacancy_detail', pk=vacancy.pk)
	else:
		form = VacancyForm()
	return render(request, 'jobpro/vacancy_edit.html', {'form': form, 'is_organisation': True})


#редактирование вакансии
@user_passes_test(is_organisation)
def vacancy_edit(request, pk):
	vacancy = get_object_or_404(Vacancy, pk=pk)
	#вакансию может редактировать только ее владелец
	if request.user == vacancy.owner:         
		if request.method == "POST":
			form = VacancyForm(request.POST, instance=vacancy)
			if form.is_valid():
				vacancy = form.save(commit=False)
				vacancy.save()
				return redirect('vacancy_detail', pk=vacancy.pk)
		else:
			form = VacancyForm(instance=vacancy)
		return render(request, 'jobpro/vacancy_edit.html', {'form': form, 'is_organisation': True})
	else:
		return redirect('/')


#удаление вакансии
@user_passes_test(is_organisation)
def vacancy_remove(request, pk):
	vacancy = get_object_or_404(Vacancy, pk=pk)
	#вакансию может удалить только ее владелец
	if request.user == vacancy.owner: 
		vacancy.delete()
		return redirect('vacancies_list')


#добавляет / удаляет вакансию в избранное
@user_passes_test(is_employee)
def vacancy_favourite_change(request):
	if request.method == "POST":
		#user = User.objects.get(username = request.user)
		user = request.user
		vacancy = Vacancy.objects.get(pk=request.POST.get("Vacancy_pk"))
		if Favourite_vacancy.objects.filter(user=user, vacancy=vacancy).exists() == False:
			new_favourite = Favourite_vacancy(
				user = user,
				vacancy = vacancy
			)
			new_favourite.save()
			return HttpResponse("add")
		else:
			remove_favourite = Favourite.objects.get(user=user, vacancy=vacancy)
			remove_favourite.delete()
			return HttpResponse("remove")
	else:
		return redirect('/')


#избранные вакансии пользователя
@user_passes_test(is_employee)
def vacancy_favourite_list(request):
	favourite_vacancies = Favourite_vacancy.objects.filter(user = request.user)
	return render(request, 'jobpro/favourite_vacancy_list.html', {'favourite_vacancies': favourite_vacancies, 'is_organisation': False})


#вакансии принадлежащие текущему пользователю
@user_passes_test(is_employee)
def my_vacancies_list(request):
	vacancies = Vacancy.objects.filter(owner = request.user)
	return render(request, 'jobpro/vacancies_list.html',{'vacancies': vacancies, 'is_organisation': False})


def cv_list(request):
	cvs = Cv.objects.filter(actual=True).order_by('pk')
	is_organisation = False
	#favourite_vacancies = None
	if request.user.is_authenticated:
		if request.user.account_type=='OR':
			is_organisation = True
		#if is_organisation == False:
			#favourite_vacancies = Favourite_vacancy.objects.filter(user = request.user)
	return render(request, 'jobpro/cv_list.html', {'cvs':cvs, 'is_organisation': is_organisation, })


def cv_detail(request, pk):
	cv = get_object_or_404(Cv, pk=pk)
	#убрать для организации
	is_owner = False
	is_favourite = False
	is_organisation = False
	if request.user.is_authenticated:
		if request.user.account_type=='OR':
			is_organisation = True
		elif cv.owner == User.objects.get(username = request.user):
			is_owner = True 
		else:
			is_favourite = Favourite_cv.objects.filter(user=request.user, cv=cv).exists()			
	return render(request, 'jobpro/cv_detail.html', {'cv': cv, 'is_organisation': is_organisation, 'is_favourite': is_favourite, 'is_owner': is_owner})



#создание резюме (резюме для каждого соискателя может быть создано только одно)
#@user_passes_test(is_employee)
def cv_new(request):
	if Cv.objects.filter(owner = request.user).exists():
		return HttpResponseRedirect(reverse('cv_list'))
	else:
		if request.method == "POST":
			form = CvForm(request.POST)
			if form.is_valid():
				cv = form.save(commit=False)
				cv.owner = request.user
				cv.created_date =  timezone.now()
				cv.save()
				return redirect('cv_detail', pk=cv.pk)
		else:
			form = CvForm()
		return render(request, 'jobpro/cv_edit.html', {'form': form, 'is_organisation': False})


#редактирование резюме
#@user_passes_test(is_employee)
def cv_edit(request, pk):
	cv = get_object_or_404(Cv, pk=pk)
	#вакансию может редактировать только ее владелец
	if request.user == cv.owner:         
		if request.method == "POST":
			form = CvForm(request.POST, instance=cv)
			if form.is_valid():
				cv = form.save(commit=False)
				cv.save()
				return redirect('cv_detail', pk=cv.pk)
		else:
			form = CvForm(instance=cv)
		return render(request, 'jobpro/cv_edit.html', {'form': form, 'is_organisation': False})
	else:
		return redirect('/')


#удаление резюме
#@user_passes_test(is_employee)
def cv_remove(request, pk):
	cv = get_object_or_404(Cv, pk=pk)
	#вакансию может удалить только ее владелец
	if request.user == cv.owner: 
		cv.delete()
		return redirect('cv_list')


#добавляет / удаляет резюме в избранное
#@user_passes_test(is_organisation)
def cv_favourite_change(request):
	if request.method == "POST":
		#user = User.objects.get(username = request.user)
		user = request.user
		cv = Cv.objects.get(pk=request.POST.get("Cv_pk"))
		if Favourite_cv.objects.filter(user=user, cv=cv).exists() == False:
			new_favourite = Favourite_cv(
				user = user,
				cv = cv
			)
			new_favourite.save()
			return HttpResponse("add")
		else:
			remove_favourite = Favourite_cv.objects.get(user=user, cv=cv)
			remove_favourite.delete()
			return HttpResponse("remove")
	else:
		return redirect('/')

#Резюме соискателя
#@user_passes_test(is_employee)
def cv_my(request):
	#если у соискателя уже есть резюме
	if Cv.objects.filter(owner=request.user).exists():
		cv = get_object_or_404(Cv, owner=request.user)
		return HttpResponseRedirect(reverse('cv_detail', args=[cv.pk]))
	else:
		return HttpResponseRedirect(reverse('cv_new'))

#избранные резюме работодателя
#@user_passes_test(is_organisation)
def cv_favourite_list(request):
	favourite_cvs = Favourite_cv.objects.filter(user = request.user)
	return render(request, 'jobpro/favourite_cv_list.html', {'favourite_cvs': favourite_cvs, 'is_organisation': is_organisation})
