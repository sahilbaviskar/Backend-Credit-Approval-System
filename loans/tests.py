from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from .models import Customer, Loan
from .utils import calculate_credit_score, calculate_monthly_installment


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="1234567890",
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000'),
            current_debt=Decimal('0')
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.first_name, "John")
        self.assertEqual(self.customer.last_name, "Doe")
        self.assertEqual(self.customer.monthly_salary, Decimal('50000'))


class LoanModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Jane",
            last_name="Smith",
            age=25,
            phone_number="9876543210",
            monthly_salary=Decimal('60000'),
            approved_limit=Decimal('2160000'),
            current_debt=Decimal('0')
        )
        
        self.loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=Decimal('10.5'),
            monthly_repayment=Decimal('8792.59'),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            emis_paid_on_time=5
        )

    def test_loan_creation(self):
        self.assertEqual(self.loan.customer, self.customer)
        self.assertEqual(self.loan.loan_amount, Decimal('100000'))
        self.assertEqual(self.loan.tenure, 12)

    def test_repayments_left(self):
        self.assertEqual(self.loan.repayments_left, 7)  # 12 - 5


class UtilsTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=28,
            phone_number="5555555555",
            monthly_salary=Decimal('40000'),
            approved_limit=Decimal('1440000'),
            current_debt=Decimal('0')
        )

    def test_calculate_monthly_installment(self):
        emi = calculate_monthly_installment(
            loan_amount=Decimal('100000'),
            interest_rate=Decimal('12'),
            tenure=12
        )
        # Should be approximately 8884.88
        self.assertAlmostEqual(float(emi), 8884.88, places=2)

    def test_calculate_credit_score_new_customer(self):
        score = calculate_credit_score(self.customer)
        self.assertEqual(score, 50)  # Default score for new customers


class APITest(APITestCase):
    def test_register_customer(self):
        url = reverse('register_customer')
        data = {
            'first_name': 'API',
            'last_name': 'Test',
            'age': 30,
            'monthly_income': 50000,
            'phone_number': '1111111111'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'API Test')
        self.assertEqual(response.data['approved_limit'], 1800000)  # 36 * 50000

    def test_register_customer_invalid_data(self):
        url = reverse('register_customer')
        data = {
            'first_name': '',  # Invalid: empty name
            'last_name': 'Test',
            'age': 30,
            'monthly_income': 50000,
            'phone_number': '1111111111'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_eligibility_new_customer(self):
        # First create a customer
        customer = Customer.objects.create(
            first_name="Eligibility",
            last_name="Test",
            age=30,
            phone_number="2222222222",
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000'),
            current_debt=Decimal('0')
        )
        
        url = reverse('check_eligibility')
        data = {
            'customer_id': customer.customer_id,
            'loan_amount': 100000,
            'interest_rate': 10,
            'tenure': 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['approval'])

    def test_create_loan(self):
        # First create a customer
        customer = Customer.objects.create(
            first_name="Loan",
            last_name="Test",
            age=30,
            phone_number="3333333333",
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000'),
            current_debt=Decimal('0')
        )
        
        url = reverse('create_loan')
        data = {
            'customer_id': customer.customer_id,
            'loan_amount': 100000,
            'interest_rate': 10,
            'tenure': 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['loan_approved'])
        self.assertIsNotNone(response.data['loan_id'])

    def test_view_loan(self):
        # Create customer and loan
        customer = Customer.objects.create(
            first_name="View",
            last_name="Test",
            age=30,
            phone_number="4444444444",
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000'),
            current_debt=Decimal('0')
        )
        
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=Decimal('10'),
            monthly_repayment=Decimal('8792.59'),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365)
        )
        
        url = reverse('view_loan', kwargs={'loan_id': loan.loan_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], loan.loan_id)

    def test_view_loans_by_customer(self):
        # Create customer and loan
        customer = Customer.objects.create(
            first_name="ViewAll",
            last_name="Test",
            age=30,
            phone_number="5555555555",
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000'),
            current_debt=Decimal('0')
        )
        
        Loan.objects.create(
            customer=customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=Decimal('10'),
            monthly_repayment=Decimal('8792.59'),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365)
        )
        
        url = reverse('view_loans_by_customer', kwargs={'customer_id': customer.customer_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)