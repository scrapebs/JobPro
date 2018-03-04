import unittest
import datetime
from django.utils import timezone
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from jobpro.models import User, Vacancy, Cv, OrgInfo

def create_cv(name, description, phone, email, owner, pk):
    created_date = timezone.now()
    return Cv.objects.create(
        name=name, 
        description=description, 
        phone=phone, 
        email=email, 
        owner=owner,
        created_date=created_date,
        pk=pk
    )

def create_org_info(name, address, phone, email, description, organisation, pk):
    created_date = timezone.now()
    return OrgInfo.objects.create(
        name=name, 
        address=address, 
        phone=phone, 
        email=email,
        description=description,
        organisation=organisation,
        pk=pk
    )

def create_vacancy(name, description, salary, owner, org_info, pk):
    created_date = timezone.now()
    return Vacancy.objects.create(
        name=name, 
        description=description, 
        salary=salary, 
        owner=owner, 
        org_info=org_info,
        created_date=created_date,
        pk=pk
    )


class not_authorized_user_completely_empty(TestCase):
    def setUp(self):
        self.client = Client()

    def test_not_authorized_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_not_authorized_vacancy_favourite_general(self):
        response = self.client.get(reverse('favourite_general'), follow=True)
        # Invitation to log in
        self.assertEqual(response.resolver_match.func.__name__, 'login')


    def test_not_authorized_cv_list(self):
        response = self.client.get(reverse('cv_list'))
        self.assertEqual(response.status_code, 200)

    def test_not_authorized_not_existing_cv_detail(self):
        response = self.client.get(reverse('cv_detail', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 404)

    def test_not_authorized_cv_new(self):
        # Invitation to log in
        response = self.client.get('/cv/new/', follow=True)
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_not_authorized_my_cv(self):
        # Invitation to log in
        response = self.client.get(reverse('cv_my'), follow=True)
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_not_authorized_cv_favourite_list(self):
        response = self.client.get(reverse('cv_favourite_list'), follow=True)
        # Invitation to log in
        self.assertEqual(response.resolver_match.func.__name__, 'login')


    def test_not_authorized_vacancies_list(self):
        response = self.client.get(reverse('vacancies_list'))
        self.assertEqual(response.status_code, 200)

    def test_not_authorized_not_existing_vacancy_detail(self):
        response = self.client.get(reverse('vacancy_detail', kwargs={'pk':1}))
        self.assertEqual(response.status_code, 404)

    def test_not_authorized_vacancy_new(self):
        response = self.client.get(reverse('vacancy_new'), follow=True)
        # Invitation to log in
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_not_authorized_my_vacancies_list(self):
        response = self.client.get(reverse('my_vacancies_list'), follow=True)
        # Invitation to log in
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_not_authorized_vacancy_favourite_list(self):
        response = self.client.get(reverse('vacancy_favourite_list'), follow=True)
        # Invitation to log in
        self.assertEqual(response.resolver_match.func.__name__, 'login')


class not_authorized_user_one_cv_exists(TestCase):
    def setUp(self):
        self.client = Client()
        some_user = User.objects.create_user(
            username='employee1', 
            email='denissinkov@mail.ru', 
            password='QT248248qt', 
            account_type='EM'
        )
        self.cv = create_cv('full name of the Employee1 user', 
                  'Description of the Employee1 user', 
                  '89098084204', 'denissinkov@mail.ru', 
                  some_user, pk = 1)

    def test_not_authorized_cv_list_of_one_cv(self):
        response = self.client.get(reverse('cv_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['cvs'], ['<Cv: ' + self.cv.name + '>'])
            
    def test_not_authorized_existing_cv_detail(self):  
        response = self.client.get(reverse('cv_detail', kwargs={'pk':1}))
        self.assertContains(response, self.cv.name, status_code=200)


class not_authorized_user_few_cvs_exist(TestCase):
    def setUp(self):
        self.client = Client()
        some_user1 = User.objects.create_user(
            username='employee1', 
            email='denissinkov@mail.ru', 
            password='QT248248qt', 
            account_type='EM'
        )
        some_user2 = User.objects.create_user(
            username='employee2', 
            email='denissinkov@mail.ru', 
            password='QT248248qt', 
            account_type='EM'
        )
        self.cv1 = create_cv('full name of the Employee1 user', 
                  'Description of the Employee1 user', 
                  '89098084204', 'denissinkov@mail.ru', 
                  some_user1, pk = 1)
        self.cv2 = create_cv('full name of the Employee2 user', 
                  'Description of the Employee2 user', 
                  '89098084204', 'denissinkov@mail.ru', 
                  some_user2, pk = 2)

    def test_not_authorized_cv_list_of_two_cv(self):
        response = self.client.get(reverse('cv_list'))
        self.assertContains(response, self.cv2.name, status_code=200)
        self.assertQuerysetEqual(response.context['cvs'], 
                                 ['<Cv: ' + self.cv1.name + '>', 
                                 '<Cv: ' + self.cv2.name + '>'])

    def test_not_authorized_existing_cv_detail(self):  
        response = self.client.get(reverse('cv_detail', kwargs={'pk':2}))
        self.assertContains(response, self.cv2.name, status_code=200)
        self.assertEqual(self.cv2.name, 'full name of the Employee2 user')


class new_employee_user_test(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='employee1', 
            email='denissinkov@mail.ru', 
            password='QT248248qt', 
            account_type='EM'
        )
        self.client.login(username='employee1', password='QT248248qt')

    def test_new_employee_cv_my(self):        
        response = self.client.get(reverse('cv_my'),  follow=True)
        # Invitation to create CV for a new employee
        self.assertEqual(response.resolver_match.func.__name__, 'cv_new')

    def test_new_employee_cv_new(self): 
        response = self.client.get(reverse('cv_new'))
        self.assertEqual(response.status_code, 200)

    def test_employee_with_created_cv_try_my_cv(self): 
        create_cv('full name of the Employee1 user', 
                  'Description of the Employee1 user', 
                  '89098084204', 'denissinkov@mail.ru', 
                  self.user, pk = 1)
        response = self.client.get(reverse('cv_my'), follow=True)
        # Redirecting to an existing CV
        self.assertEqual(response.resolver_match.func.__name__, 'cv_detail')

    def test_employee_with_created_cv_try_new_cv(self): 
        create_cv('full name of the Employee1 user', 
                  'Description of the Employee1 user', 
                  '89098084204', 'denissinkov@mail.ru', 
                  self.user, pk=1)    
        response = self.client.get(reverse('cv_new'), follow=True)
        # Redirecting to an existing CV
        self.assertEqual(response.resolver_match.func.__name__, 'cv_detail')

    def test_employee_with_created_cv_try_cv_detail(self):  
        cv = create_cv('full name of the employee1 user', 
                  'Description of the employee1 user', 
                  '89098084204', 'denissinkov@mail.ru', 
                  self.user, pk = 1)
        response = self.client.get(reverse('cv_detail', args=(cv.pk,)))
        self.assertContains(response, cv.name, status_code=200)
        
    def test_employee_try_vacancy_new(self):
        response = self.client.get(reverse('vacancy_new'), follow=True)
        # Invitation to re-register
        # Employee can't create his own vacancies
        self.assertEqual(response.resolver_match.func.__name__, 'login')

    def test_not_authorized_my_vacancies_list(self):
        response = self.client.get(reverse('my_vacancies_list'), follow=True)
        # Invitation to re-register
        # Employee can't create his own vacancies
        self.assertEqual(response.resolver_match.func.__name__, 'login')    


class new_employer_user_test(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='employer1', 
            email='denissinkov@mail.ru', 
            password='QT248248qt', 
            account_type='OR'
        )
        self.client.login(username='employer1', password='QT248248qt')

    def test_new_employer_without_org_info_try_vacancy_my(self):        
        response = self.client.get(reverse('vacancy_new'),  follow=True)
        # Employer should firstly fill organisation_info
        self.assertEqual(response.resolver_match.func.__name__, 'org_info_new')

    def test_new_employee_org_info_new(self): 
        response = self.client.get(reverse('org_info_new'))
        self.assertEqual(response.status_code, 200)

    def test_new_employer_create_org_info(self):       
        org_info = create_org_info('Name of the Employer organisation', 
                        'address of the employer\'s organisation',
                        '89098084204', 'denissinkov@mail.ru', 
                        'Description of the employer\'s organisation',
                        self.user, pk=1)
        response = self.client.get(reverse('org_info_detail', args=(org_info.pk,)))
        self.assertEqual(response.status_code, 200)
        
    def test_new_employer_with_org_info_create_new_vacancy(self):       
        org_info = create_org_info('Name of the Employer organisation', 
                        'address of the Employer\'s organisation',
                        '89098084204', 'denissinkov@mail.ru', 
                        'Description of the Employer\'s organisation',
                        self.user, pk=1)
        response = self.client.get(reverse('vacancy_new'))
        self.assertEqual(response.status_code, 200)
        vacancy = create_vacancy('Name of the vacancy','Description of the vacancy',
                                 70000, self.user, org_info, pk=1)
        response = self.client.get(reverse('vacancy_detail', args=(vacancy.pk,)))
        self.assertEqual(response.status_code, 200)
        
    def test_employer_cv_my(self):        
        response = self.client.get(reverse('cv_my'),  follow=True)
        # Invitation to re-register
        # Employer can't create a CV
        self.assertEqual(response.resolver_match.func.__name__, 'login') 

    def test_employer_cv_new(self): 
        response = self.client.get(reverse('cv_new'), follow=True)
        # Invitation to re-register
        # Employer can't create a CV
        self.assertEqual(response.resolver_match.func.__name__, 'login') 


