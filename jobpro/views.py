from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.db import transaction 
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.views import generic

from jobpro.models import User, Vacancy, Cv, FavouriteVacancy, FavouriteCv, OrgInfo  
from jobpro.forms import VacancyForm, CvForm, OrgInfoForm


# Decorator verifying that the user is an organization
def is_organisation(user):
    if user.is_authenticated: 
        return user.account_type == 'OR'
    else:
        return False

# Decorator verifying that the user is an employee
def is_employee(user):
    if user.is_authenticated: 
        return user.account_type == 'EM'
    else:
        return False

# Main page
def index(request):
    if request.user.is_authenticated == True: 
        return render(request, 'jobpro/index.html', {}, )
    else:
        return render(request, 'jobpro/index_logout.html', {}, )

# List of all vacancies
def vacancies_list(request):
    vacancies = Vacancy.objects.filter(actual=True).order_by('name')
    """favourite_vacancies is None
    if request.user.is_authenticated:
        if request.user.account_type=='EM':
            favourite_vacancies = FavouriteVacancy.objects.filter(user = request.user)"""
    return render(request, 'jobpro/vacancies_list.html', {'vacancies':vacancies}, )

# Information of the selected vacancy
def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    is_owner = False
    is_favourite = False
    if request.user.is_authenticated:
        if request.user.account_type =='OR':
            if vacancy.owner == User.objects.get(username = request.user):
                is_owner = True 
        else:
            is_favourite = FavouriteVacancy.objects.filter(user=request.user, vacancy=vacancy).exists()            
    return render(request, 'jobpro/vacancy_detail.html', {'vacancy': vacancy, 'is_favourite': is_favourite, 'is_owner': is_owner})

# Creating new vacancy
@user_passes_test(is_organisation)
def vacancy_new(request):
    if OrgInfo.objects.filter(organisation=request.user).exists():
        if request.method == "POST":
            form = VacancyForm(request.POST)
            if form.is_valid():
                vacancy = form.save(commit=False)
                vacancy.owner = request.user
                vacancy.created_date = timezone.now()
                vacancy.org_info = request.user.info
                vacancy.save()
                return redirect('vacancy_detail', pk=vacancy.pk)
        else:
            form = VacancyForm()
        return render(request, 'jobpro/vacancy_edit.html', {'form': form})
    else:
        return HttpResponseRedirect(reverse('org_info_new'))

# Editing vacancy
@user_passes_test(is_organisation)
def vacancy_edit(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
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

# Deleting vacancy
@require_http_methods(["POST"])
@user_passes_test(is_organisation)
def vacancy_remove(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    if request.user == vacancy.owner: 
        vacancy.delete()
        return redirect('vacancies_list')

# Adding / removing a vacancy to the favorites
@user_passes_test(is_employee)
def vacancy_favourite_change(request):
    if request.method == "POST":
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
            remove_favourite = FavouriteVacancy.objects.get(user=user, vacancy=vacancy)
            remove_favourite.delete()
            return HttpResponse("remove")
    return HttpResponseRedirect(reverse('index'))

# Favourite vacancies of the user (employee)
@user_passes_test(is_employee)
def vacancy_favourite_list(request):
    favourite_vacancies = FavouriteVacancy.objects.filter(user=request.user)
    return render(request, 'jobpro/favourite_vacancy_list.html', {'favourite_vacancies': favourite_vacancies})

# Vacancies belonging to the current user (organistion)
@user_passes_test(is_organisation)
def my_vacancies_list(request):
    vacancies = Vacancy.objects.filter(owner=request.user)
    return render(request, 'jobpro/vacancies_list.html',{'vacancies': vacancies, 'description': 'Ваши вакансии'}, )

# Vacancies of a selected organization
def org_vacancies_list(request, pk):
    vacancies = Vacancy.objects.filter(owner=pk)
    return render(request, 'jobpro/vacancies_list.html',{'vacancies': vacancies, 'description': 'Вакансии'}, )

# List of CVs
def cv_list(request):
    cvs = Cv.objects.filter(actual=True).order_by('pk') 
    return render(request, 'jobpro/cv_list.html', {'cvs': cvs })

# List of CVs by generic
class CvView(generic.ListView):
    template_name = 'jobpro/cv_list.html'
    context_object_name = 'cvs_list'

    def get_queryset(self):
        Cv.objects.filter(actual=True).order_by('pk')

# Information of the selected CV
def cv_detail(request, pk):
    cv = get_object_or_404(Cv, pk=pk)
    is_owner = False
    is_favourite = False
    is_organisation = False
    if request.user.is_authenticated:
        if request.user.account_type=='OR':
            is_organisation = True
            is_favourite = FavouriteCv.objects.filter(user=request.user, cv=cv).exists()
        elif cv.owner == User.objects.get(username = request.user):
            is_owner = True                         
    return render(request, 'jobpro/cv_detail.html', {'cv': cv, 'is_organisation': is_organisation, 'is_favourite': is_favourite, 'is_owner': is_owner})

# Creating a resume (a resume for each applicant can be created only one)
@user_passes_test(is_employee)
def cv_new(request):
    if Cv.objects.filter(owner = request.user).exists():
        return HttpResponseRedirect(reverse('cv_my'))
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

# Editing CV
@user_passes_test(is_employee)
def cv_edit(request, pk):
    cv = get_object_or_404(Cv, pk=pk)
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

# Deleting CV
@require_http_methods(["POST"])
@user_passes_test(is_employee)
def cv_remove(request, pk):
    cv = get_object_or_404(Cv, pk=pk)
    #резюме может удалить только его владелец
    if request.user == cv.owner: 
        cv.delete()
        return redirect('cv_list')


# Adding / removing a CV to the favorites
@user_passes_test(is_organisation)
def cv_favourite_change(request):
    if request.method == "POST":
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

# CV of the current user (employee)
@user_passes_test(is_employee)
def cv_my(request):
    # If employee already has a CV
    if Cv.objects.filter(owner=request.user).exists():
        cv = get_object_or_404(Cv, owner=request.user)
        return HttpResponseRedirect(reverse('cv_detail', args=[cv.pk]))
    else:
        return HttpResponseRedirect(reverse('cv_new'))

# Favourite vacancies of the user (organisation)
@user_passes_test(is_organisation)
def cv_favourite_list(request):
    favourite_cvs = FavouriteCv.objects.filter(user=request.user)
    return render(request, 'jobpro/favourite_cv_list.html', {'favourite_cvs': favourite_cvs})


# Information about the employer
def org_info_detail(request, pk):
    org_info = get_object_or_404(OrgInfo, pk=pk)        
    is_owner = False
    if request.user.is_authenticated:
        if request.user.account_type == 'OR':
            if org_info.organisation == request.user:
                is_owner = True 
    return render(request, 'jobpro/org_info_detail.html', {'org_info': org_info, 'is_owner': is_owner})

# Adding information about the employer
@user_passes_test(is_organisation)
def org_info_new(request):
    if OrgInfo.objects.filter(organisation=request.user).exists():
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

# Editing information about the employer
@user_passes_test(is_organisation)
def org_info_edit(request, pk):
    org_info = get_object_or_404(OrgInfo, pk=pk)
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

# Deleting information about the employer
@require_http_methods(["POST"])
@user_passes_test(is_organisation)
def org_info_remove(request, pk):
    org_info = get_object_or_404(OrgInfo, pk=pk)
    if request.user == org_info.organisation: 
        org_info.delete()
        return redirect('index')

# Information about the current user-employer
@user_passes_test(is_organisation)
def org_info_my(request):
    #если у соискателя уже есть резюме
    if OrgInfo.objects.filter(organisation=request.user).exists():
        org_info = get_object_or_404(OrgInfo, organisation=request.user)
        return HttpResponseRedirect(reverse('org_info_detail', args=[org_info.pk]))
    else:
        return HttpResponseRedirect(reverse('org_info_new'))

# Transition from a vacancy to an employer
def org_info_vacancy(request, owner_pk):
    org_info = get_object_or_404(OrgInfo, organisation=owner_pk)
    return HttpResponseRedirect(reverse('org_info_detail', args=[org_info.pk]))

# For the employee returns a list of selected vacancies. For the employer returns a list of selected CVs.
@login_required
def favourite_general(request):
    if request.user.is_authenticated:
        if request.user.account_type == 'OR':
            return HttpResponseRedirect(reverse('cv_favourite_list'))
        else:
            return HttpResponseRedirect(reverse('vacancy_favourite_list'))
