import math
from decimal import Decimal
from datetime import datetime, date
from django.db.models import Sum, Q
from .models import Customer, Loan


def calculate_credit_score(customer):
    """
    Calculate credit score based on historical loan data
    Components:
    1. Past Loans paid on time
    2. Number of loans taken in past
    3. Loan activity in current year
    4. Loan approved volume
    5. If sum of current loans > approved limit, credit score = 0
    """
    loans = Loan.objects.filter(customer=customer)
    
    if not loans.exists():
        return 50  # Default score for new customers
    
    # Check if current loans exceed approved limit
    current_loans_sum = loans.filter(is_active=True).aggregate(
        total=Sum('loan_amount')
    )['total'] or 0
    
    if current_loans_sum > customer.approved_limit:
        return 0
    
    # Calculate components
    total_loans = loans.count()
    if total_loans == 0:
        return 50
    
    # 1. Past loans paid on time (40% weight)
    on_time_payments = 0
    total_payments = 0
    for loan in loans:
        total_payments += loan.tenure
        on_time_payments += loan.emis_paid_on_time
    
    on_time_ratio = on_time_payments / total_payments if total_payments > 0 else 0
    on_time_score = on_time_ratio * 40
    
    # 2. Number of loans taken (20% weight) - fewer loans is better
    loan_count_score = max(0, 20 - (total_loans * 2))
    
    # 3. Loan activity in current year (20% weight)
    current_year = datetime.now().year
    current_year_loans = loans.filter(start_date__year=current_year).count()
    activity_score = max(0, 20 - (current_year_loans * 5))
    
    # 4. Loan approved volume vs limit (20% weight)
    volume_ratio = current_loans_sum / customer.approved_limit if customer.approved_limit > 0 else 0
    volume_score = max(0, 20 - (volume_ratio * 20))
    
    total_score = float(on_time_score) + float(loan_count_score) + float(activity_score) + float(volume_score)
    return min(100, max(0, total_score))


def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    """
    Calculate monthly installment using compound interest formula
    EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
    """
    principal = float(loan_amount)
    monthly_rate = float(interest_rate) / (12 * 100)  # Convert annual rate to monthly decimal
    
    if monthly_rate == 0:
        return Decimal(principal / tenure)
    
    emi = principal * monthly_rate * (1 + monthly_rate) ** tenure / ((1 + monthly_rate) ** tenure - 1)
    return Decimal(round(emi, 2))


def get_corrected_interest_rate(credit_score, requested_rate):
    """
    Get corrected interest rate based on credit score
    """
    if credit_score > 50:
        return max(requested_rate, Decimal('0.00'))  # Any rate is fine
    elif 30 < credit_score <= 50:
        return max(requested_rate, Decimal('12.00'))
    elif 10 < credit_score <= 30:
        return max(requested_rate, Decimal('16.00'))
    else:
        return None  # Loan not approved


def check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure):
    """
    Check loan eligibility based on credit score and other criteria
    """
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return {
            'approval': False,
            'message': 'Customer not found',
            'interest_rate': interest_rate,
            'corrected_interest_rate': interest_rate,
            'monthly_installment': 0
        }
    
    credit_score = calculate_credit_score(customer)
    
    # Check if credit score allows loan approval
    if credit_score <= 10:
        return {
            'approval': False,
            'message': 'Credit score too low',
            'interest_rate': interest_rate,
            'corrected_interest_rate': interest_rate,
            'monthly_installment': 0
        }
    
    # Get corrected interest rate
    corrected_rate = get_corrected_interest_rate(credit_score, interest_rate)
    if corrected_rate is None:
        return {
            'approval': False,
            'message': 'Credit score too low',
            'interest_rate': interest_rate,
            'corrected_interest_rate': interest_rate,
            'monthly_installment': 0
        }
    
    # Calculate monthly installment with corrected rate
    monthly_installment = calculate_monthly_installment(loan_amount, corrected_rate, tenure)
    
    # Check if sum of all current EMIs > 50% of monthly salary
    current_emis = Loan.objects.filter(
        customer=customer, 
        is_active=True
    ).aggregate(total=Sum('monthly_repayment'))['total'] or 0
    
    total_emis = current_emis + monthly_installment
    if total_emis > (customer.monthly_salary * Decimal('0.5')):
        return {
            'approval': False,
            'message': 'Total EMIs exceed 50% of monthly salary',
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_rate,
            'monthly_installment': monthly_installment
        }
    
    return {
        'approval': True,
        'message': 'Loan approved',
        'interest_rate': interest_rate,
        'corrected_interest_rate': corrected_rate,
        'monthly_installment': monthly_installment
    }