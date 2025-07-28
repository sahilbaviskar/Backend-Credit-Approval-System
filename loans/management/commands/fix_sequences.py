from django.core.management.base import BaseCommand
from django.db import connection, models
from loans.models import Customer, Loan


class Command(BaseCommand):
    help = 'Fix PostgreSQL sequences for auto-incrementing fields'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Fix customer_id sequence
            max_customer_id = Customer.objects.aggregate(
                max_id=models.Max('customer_id')
            )['max_id'] or 0
            
            cursor.execute(
                "SELECT setval('customers_customer_id_seq', %s, true);",
                [max_customer_id]
            )
            
            # Fix loan_id sequence
            max_loan_id = Loan.objects.aggregate(
                max_id=models.Max('loan_id')
            )['max_id'] or 0
            
            cursor.execute(
                "SELECT setval('loans_loan_id_seq', %s, true);",
                [max_loan_id]
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sequences fixed: customer_id starts from {max_customer_id + 1}, '
                    f'loan_id starts from {max_loan_id + 1}'
                )
            )