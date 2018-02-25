from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils import timezone
from .models import User, Vacancy, Cv, FavouriteVacancy, FavouriteCv, OrgInfo  
from .forms import VacancyForm, CvForm, OrgInfoForm
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
	favourite_vacancies = None
	if request.user.is_authenticated:
		if request.user.account_type=='EM':
			favourite_vacancies = FavouriteVacancy.objects.filter(user = request.user)
	return render(request, 'jobpro/vacancies_list.html', {'vacancies':vacancies, 'favourite_vacancies': favourite_vacancies}, )


#информация по выбранной вакансии
def vacancy_detail(request, pk):
	vacancy = get_object_or_404(Vacancy, pk=pk)
	#убрать для организации
	is_owner = False
	is_favourite = False
	if request.user.is_authenticated:
		if request.user.account_type=='OR':
			if vacancy.owner == User.objects.get(username = request.user):
				is_owner = True 
		else:
			is_favourite = FavouriteVacancy.objects.filter(user=request.user, vacancy=vacancy).exists()			
	return render(request, 'jobpro/vacancy_detail.html', {'vacancy': vacancy, 'is_favourite': is_favourite, 'is_owner': is_owner})


#заведение новой вакансии
@user_passes_test(is_organisation)
def vacancy_new(request):
	if OrgInfo.objects.filter(organisation=request.user).exists():
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
		return render(request, 'jobpro/vacancy_edit.html', {'form': form})
	else:
		return HttpResponseRedirect(reverse('org_info_new'))


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
		return render(request, 'jobpro/vacancy_edit.html', {'form': form})
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
		if FavouriteVacancy.objects.filter(user=user, vacancy=vacancy).exists() == False:
			new_favourite = FavouriteVacancy(
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
	favourite_vacancies = FavouriteVacancy.objects.filter(user = request.user)
	return render(request, 'jobpro/favourite_vacancy_list.html', {'favourite_vacancies': favourite_vacancies})


#вакансии принадлежащие текущему пользователю
@user_passes_test(is_organisation)
def my_vacancies_list(request):
	vacancies = Vacancy.objects.filter(owner = request.user)
	return render(request, 'jobpro/vacancies_list.html',{'vacancies': vacancies})


def cv_list(request):
	cvs = Cv.objects.filter(actual=True).order_by('pk')
	is_organisation = False
	#favourite_vacancies = None
		#if is_organisation == False:
			#favourite_vacancies = FavouriteVacancy.objects.filter(user = request.user)
	return render(request, 'jobpro/cv_list.html', {'cvs':cvs })


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
			is_favourite = FavouriteCv.objects.filter(user=request.user, cv=cv).exists()			
	return render(request, 'jobpro/cv_detail.html', {'cv': cv, 'is_organisation': is_organisation, 'is_favourite': is_favourite, 'is_owner': is_owner})



#создание резюме (резюме для каждого соискателя может быть создано только одно)
@user_passes_test(is_employee)
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
		return render(request, 'jobpro/cv_edit.html', {'form': form})


#редактирование резюме
@user_passes_test(is_employee)
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
		return render(request, 'jobpro/cv_edit.html', {'form': form})
	else:
		return redirect('/')


#удаление резюме
@user_passes_test(is_employee)
def cv_remove(request, pk):
	cv = get_object_or_404(Cv, pk=pk)
	#резюме может удалить только его владелец
	if request.user == cv.owner: 
		cv.delete()
		return redirect('cv_list')


#добавляет / удаляет резюме в избранное
@user_passes_test(is_organisation)
def cv_favourite_change(request):
	if request.method == "POST":
		#user = User.objects.get(username = request.user)
		user = request.user
		cv = Cv.objects.get(pk=request.POST.get("Cv_pk"))
		if FavouriteCv.objects.filter(user=user, cv=cv).exists() == False:
			new_favourite = FavouriteCv(
				user = user,
				cv = cv
			)
			new_favourite.save()
			return HttpResponse("add")
		else:
			remove_favourite = FavouriteCv.objects.get(user=user, cv=cv)
			remove_favourite.delete()
			return HttpResponse("remove")
	else:
		return redirect('/')

#Резюме соискателя
@user_passes_test(is_employee)
def cv_my(request):
	#если у соискателя уже есть резюме
	if Cv.objects.filter(owner=request.user).exists():
		cv = get_object_or_404(Cv, owner=request.user)
		return HttpResponseRedirect(reverse('cv_detail', args=[cv.pk]))
	else:
		return HttpResponseRedirect(reverse('cv_new'))

#избранные резюме работодателя
@user_passes_test(is_organisation)
def cv_favourite_list(request):
	favourite_cvs = FavouriteCv.objects.filter(user = request.user)
	return render(request, 'jobpro/favourite_cv_list.html', {'favourite_cvs': favourite_cvs})

#информация об работодателе
def org_info_detail(request, pk):
	org_info = get_object_or_404(OrgInfo, pk=pk)		
	is_owner = False
	if request.user.is_authenticated:
		if request.user.account_type == 'OR':
			if org_info.organisation == request.user:
				is_owner = True 
	return render(request, 'jobpro/org_info_detail.html', {'org_info': org_info, 'is_owner': is_owner})

#добавление информации о работодателе
@user_passes_test(is_organisation)
def org_info_new(request):
	if OrgInfo.objects.filter(organisation = request.user).exists():
		return HttpResponseRedirect(reverse('index'))
	else:
		if request.method == "POST":
			form = OrgInfoForm(request.POST)
			if form.is_valid():
				org_info = form.save(commit=False)
				org_info.organisation = request.user
				org_info.created_date =  timezone.now()
				org_info.save()
				return redirect('org_info_detail', pk=org_info.pk)
		else:
			form = OrgInfoForm()
		return render(request, 'jobpro/org_info_edit.html', {'form': form})


#редактирование информации о работодателе
@user_passes_test(is_organisation)
def org_info_edit(request, pk):
	org_info = get_object_or_404(OrgInfo, pk=pk)
	#вакансию может редактировать только ее владелец
	if request.user == org_info.organisation:         
		if request.method == "POST":
			form = OrgInfoForm(request.POST, instance=org_info)
			if form.is_valid():
				org_info = form.save(commit=False)
				org_info.save()
				return redirect('org_info_detail', pk=org_info.pk)
		else:
			form = OrgInfoForm(instance=org_info)
		return render(request, 'jobpro/org_info_edit.html', {'form': form})
	else:
		return redirect('/')


#удаление информации о работодателе
@user_passes_test(is_organisation)
def org_info_remove(request, pk):
	org_info = get_object_or_404(OrgInfo, pk=pk)
	if request.user == org_info.organisation: 
		org_info.delete()
		return redirect('index')


@user_passes_test(is_organisation)
def org_info_my(request):
	#если у соискателя уже есть резюме
	if OrgInfo.objects.filter(organisation=request.user).exists():
		org_info = get_object_or_404(OrgInfo, organisation=request.user)
		return HttpResponseRedirect(reverse('org_info_detail', args=[org_info.pk]))
	else:
		return HttpResponseRedirect(reverse('org_info_new'))

def org_info_vacancy(request, owner_pk):
	org_info = get_object_or_404(OrgInfo, organisation=owner_pk)
	return HttpResponseRedirect(reverse('org_info_detail', args=[org_info.pk]))

@login_required
def favourite_general(request):
	if request.user.is_authenticated:
		if request.user.account_type=='OR':
			return HttpResponseRedirect(reverse('cv_favourite_list'))
		else:
			return HttpResponseRedirect(reverse('vacancy_favourite_list'))
