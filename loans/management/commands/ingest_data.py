from django.core.management.base import BaseCommand
from loans.tasks import ingest_all_data


class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data ingestion...'))
        
        result = ingest_all_data()
        
        self.stdout.write(self.style.SUCCESS('Data ingestion completed!'))
        self.stdout.write(f"Customer ingestion: {result['customer_ingestion']}")
        self.stdout.write(f"Loan ingestion: {result['loan_ingestion']}")