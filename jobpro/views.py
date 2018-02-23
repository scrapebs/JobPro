from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Vacancy, Favourite  
#from django.contrib.auth.models import User
from .forms import VacancyForm #UserForm, ProfileForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction 
from django.contrib.auth import authenticate, login
from django.http import HttpResponse


"""
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('settings:profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        #user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'registration/registration_form_new.html', {
        #'user_form': user_form,
        'profile_form': profile_form
    })"""


def index(request):
	return render(request, 'jobpro/index.html', {}, )

#список вакансий
def vacancies_list(request):
	vacancies = Vacancy.objects.filter(actual=True).order_by('name')
	return render(request, 'jobpro/vacancies_list.html', {'vacancies':vacancies, 'vacancies_num':vacancies.count()}, )


#информация по выбранной вакансии
def vacancy_detail(request, pk):
	vacancy = get_object_or_404(Vacancy, pk=pk)
	#убрать для организации
	is_owner = False
	is_favourite = False
	if request.user.is_authenticated == True: 
		is_favourite = Favourite.objects.filter(user=request.user, vacancy=vacancy).exists()
		if vacancy.owner == User.objects.get(username = request.user):
			is_owner = True 
		else:
			is_owner = False				
	return render(request, 'jobpro/vacancy_detail.html', {'vacancy': vacancy, 'is_favourite': is_favourite, 'is_owner': is_owner})


#заведение новой вакансии
@login_required
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
@login_required
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
@login_required
def vacancy_remove(request, pk):
	vacancy = get_object_or_404(Vacancy, pk=pk)
	#вакансию может удалить только ее владелец
	if request.user == vacancy.owner: 
		vacancy.delete()
		return redirect('vacancies_list')


#добавляет / удаляет вакансию в избранное
@login_required
def vacancy_favourite_change(request):
	if request.method == "POST":
		#user = User.objects.get(username = request.user)
		user = request.user
		vacancy = Vacancy.objects.get(name=request.POST.get("Vacancy"))
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
@login_required
def favourite_list(request):
	favourite_vacancies = Favourite.objects.filter(user = request.user)
	return render(request, 'jobpro/favourite_list.html', {'favourite_vacancies': favourite_vacancies, 'favourite_vacancies_num': favourite_vacancies.count()})


#вакансии принадлежащие текущему пользователю
@login_required
def my_vacancies_list(request):
	vacancies = Vacancy.objects.filter(owner = request.user)
	return render(request, 'jobpro/vacancies_list.html',{'vacancies': vacancies})
