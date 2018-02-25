from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Vacancy, Favourite  
from .models import User
from .forms import VacancyForm #UserForm, ProfileForm
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
	is_authenticated = request.user.is_authenticated
	if is_authenticated == True:
		is_organisation = User.objects.filter(username = request.user, account_type='OR').exists()
		if is_organisation == False:
			favourite_vacancies = Favourite.objects.filter(user = request.user)
	return render(request, 'jobpro/vacancies_list.html', {'vacancies':vacancies, 'is_authenticated': is_authenticated, 'is_organisation': is_organisation, 'favourite_vacancies': favourite_vacancies}, )


#информация по выбранной вакансии
def vacancy_detail(request, pk):
	vacancy = get_object_or_404(Vacancy, pk=pk)
	#убрать для организации
	is_owner = False
	is_favourite = False
	is_organisation = False
	is_authenticated = request.user.is_authenticated
	if is_authenticated == True:
		#is_organisation = User.objects.filter(username = request.user, account_type='OR').exists()
		if request.user.account_type=='OR':
			is_organisation = True
			if vacancy.owner == User.objects.get(username = request.user):
				is_owner = True 
		else:
			is_favourite = Favourite.objects.filter(user=request.user, vacancy=vacancy).exists()			
	return render(request, 'jobpro/vacancy_detail.html', {'vacancy': vacancy, 'is_authenticated': is_authenticated, 'is_organisation': is_organisation, 'is_favourite': is_favourite, 'is_owner': is_owner})


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
	return render(request, 'jobpro/vacancy_edit.html', {'form': form})


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
		if Favourite.objects.filter(user=user, vacancy=vacancy).exists() == False:
			new_favourite = Favourite(
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
	favourite_vacancies = Favourite.objects.filter(user = request.user)
	return render(request, 'jobpro/favourite_list.html', {'favourite_vacancies': favourite_vacancies, 'favourite_vacancies_num': favourite_vacancies.count()})


#вакансии принадлежащие текущему пользователю
#@user_passes_test(is_employee)
def my_vacancies_list(request):
	vacancies = Vacancy.objects.filter(owner = request.user)
	return render(request, 'jobpro/vacancies_list.html',{'vacancies': vacancies})

"""
class OrganisationRequiredMixin(object):
	def dispatch(self, request, *args, **kwargs):
		if request.user.account_type != 'OR':
			raise PermissionDenied
		return super(OrganisationRequiredMixin, self).dispatch(request, *args, **kwargs)

class OrganisationView(OrganisationRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Vasya molodec')
        """