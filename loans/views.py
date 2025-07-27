from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import connection
from datetime import date, timedelta
from decimal import Decimal
import redis
from django.conf import settings

from .models import Customer, Loan
from .serializers import (
    CustomerRegistrationSerializer,
    CustomerRegistrationResponseSerializer,
    LoanEligibilitySerializer,
    LoanEligibilityResponseSerializer,
    LoanCreateSerializer,
    LoanCreateResponseSerializer,
    LoanDetailSerializer,
    LoanListSerializer
)
from .utils import check_loan_eligibility, calculate_monthly_installment


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint with database and Redis connectivity checks
    """
    health_status = {
        'status': 'healthy',
        'message': 'Credit Approval System is running',
        'timestamp': date.today().isoformat(),
        'services': {}
    }
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check Redis connectivity
    try:
        redis_client = redis.from_url(settings.CELERY_BROKER_URL)
        redis_client.ping()
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Return appropriate status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)


@api_view(['POST'])
def register_customer(request):
    """
    Register a new customer
    """
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        response_serializer = CustomerRegistrationResponseSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_eligibility(request):
    """
    Check loan eligibility for a customer
    """
    serializer = LoanEligibilitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    eligibility_result = check_loan_eligibility(
        data['customer_id'],
        data['loan_amount'],
        data['interest_rate'],
        data['tenure']
    )
    
    response_data = {
        'customer_id': data['customer_id'],
        'approval': eligibility_result['approval'],
        'interest_rate': eligibility_result['interest_rate'],
        'corrected_interest_rate': eligibility_result['corrected_interest_rate'],
        'tenure': data['tenure'],
        'monthly_installment': eligibility_result['monthly_installment']
    }
    
    response_serializer = LoanEligibilityResponseSerializer(response_data)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_loan(request):
    """
    Create a new loan if eligible
    """
    serializer = LoanCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Check eligibility first
    eligibility_result = check_loan_eligibility(
        data['customer_id'],
        data['loan_amount'],
        data['interest_rate'],
        data['tenure']
    )
    
    if not eligibility_result['approval']:
        response_data = {
            'loan_id': None,
            'customer_id': data['customer_id'],
            'loan_approved': False,
            'message': eligibility_result['message'],
            'monthly_installment': None
        }
        response_serializer = LoanCreateResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    # Create the loan
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
        
        # Calculate dates
        start_date = date.today()
        end_date = start_date + timedelta(days=data['tenure'] * 30)  # Approximate
        
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=data['loan_amount'],
            tenure=data['tenure'],
            interest_rate=eligibility_result['corrected_interest_rate'],
            monthly_repayment=eligibility_result['monthly_installment'],
            start_date=start_date,
            end_date=end_date
        )
        
        # Update customer's current debt
        customer.current_debt += data['loan_amount']
        customer.save()
        
        response_data = {
            'loan_id': loan.loan_id,
            'customer_id': data['customer_id'],
            'loan_approved': True,
            'message': 'Loan approved successfully',
            'monthly_installment': eligibility_result['monthly_installment']
        }
        
        response_serializer = LoanCreateResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except Customer.DoesNotExist:
        response_data = {
            'loan_id': None,
            'customer_id': data['customer_id'],
            'loan_approved': False,
            'message': 'Customer not found',
            'monthly_installment': None
        }
        response_serializer = LoanCreateResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def view_loan(request, loan_id):
    """
    View loan details by loan ID
    """
    try:
        loan = Loan.objects.select_related('customer').get(loan_id=loan_id)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Loan not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    """
    View all loans for a specific customer
    """
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer, is_active=True)
        serializer = LoanListSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )