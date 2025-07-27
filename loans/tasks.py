import pandas as pd
from celery import shared_task
from django.conf import settings
from datetime import datetime
from decimal import Decimal
import os

from .models import Customer, Loan


@shared_task
def ingest_customer_data():
    """
    Ingest customer data from Excel file
    """
    try:
        # Read customer data
        customer_file_path = os.path.join(settings.BASE_DIR, 'customer_data.xlsx')
        df = pd.read_excel(customer_file_path)
        
        customers_created = 0
        customers_updated = 0
        
        for _, row in df.iterrows():
            customer_data = {
                'customer_id': int(row['Customer ID']),
                'first_name': str(row['First Name']),
                'last_name': str(row['Last Name']),
                'phone_number': str(row['Phone Number']),
                'monthly_salary': Decimal(str(row['Monthly Salary'])),
                'approved_limit': Decimal(str(row['Approved Limit'])),
                'current_debt': Decimal('0'),  # Default since not in Excel
                'age': int(row['Age']) if 'Age' in row and pd.notna(row['Age']) else 25
            }
            
            customer, created = Customer.objects.update_or_create(
                customer_id=customer_data['customer_id'],
                defaults=customer_data
            )
            
            if created:
                customers_created += 1
            else:
                customers_updated += 1
        
        return {
            'status': 'success',
            'customers_created': customers_created,
            'customers_updated': customers_updated,
            'total_processed': len(df)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def ingest_loan_data():
    """
    Ingest loan data from Excel file
    """
    try:
        # Read loan data
        loan_file_path = os.path.join(settings.BASE_DIR, 'loan_data.xlsx')
        df = pd.read_excel(loan_file_path)
        
        loans_created = 0
        loans_updated = 0
        
        for _, row in df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=int(row['Customer ID']))
                
                # Parse dates
                start_date = pd.to_datetime(row['Date of Approval']).date()
                end_date = pd.to_datetime(row['End Date']).date()
                
                loan_data = {
                    'loan_id': int(row['Loan ID']),
                    'customer': customer,
                    'loan_amount': Decimal(str(row['Loan Amount'])),
                    'tenure': int(row['Tenure']),
                    'interest_rate': Decimal(str(row['Interest Rate'])),
                    'monthly_repayment': Decimal(str(row['Monthly payment'])),
                    'emis_paid_on_time': int(row['EMIs paid on Time']),
                    'start_date': start_date,
                    'end_date': end_date,
                    'is_active': end_date > datetime.now().date()
                }
                
                loan, created = Loan.objects.update_or_create(
                    loan_id=loan_data['loan_id'],
                    defaults=loan_data
                )
                
                if created:
                    loans_created += 1
                else:
                    loans_updated += 1
                    
            except Customer.DoesNotExist:
                print(f"Customer with ID {row['Customer ID']} not found for loan {row['Loan ID']}")
                continue
            except Exception as e:
                print(f"Error processing loan {row['Loan ID']}: {str(e)}")
                continue
        
        return {
            'status': 'success',
            'loans_created': loans_created,
            'loans_updated': loans_updated,
            'total_processed': len(df)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def ingest_all_data():
    """
    Ingest both customer and loan data
    """
    customer_result = ingest_customer_data()
    loan_result = ingest_loan_data()
    
    return {
        'customer_ingestion': customer_result,
        'loan_ingestion': loan_result
    }