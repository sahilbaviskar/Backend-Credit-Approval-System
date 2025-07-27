@echo off
echo Verifying data in the database...
echo.

echo Checking customer count:
docker-compose exec web python manage.py shell -c "from loans.models import Customer; print(f'Total customers: {Customer.objects.count()}')"

echo.
echo Checking loan count:
docker-compose exec web python manage.py shell -c "from loans.models import Loan; print(f'Total loans: {Loan.objects.count()}')"

echo.
echo Sample customer data:
docker-compose exec web python manage.py shell -c "from loans.models import Customer; c = Customer.objects.first(); print(f'Customer ID: {c.customer_id}, Name: {c.first_name} {c.last_name}, Salary: {c.monthly_salary}')"

echo.
echo Sample loan data:
docker-compose exec web python manage.py shell -c "from loans.models import Loan; l = Loan.objects.first(); print(f'Loan ID: {l.loan_id}, Amount: {l.loan_amount}, Customer: {l.customer.first_name} {l.customer.last_name}')"

echo.
echo Data verification complete!
echo You can now access the admin interface at: http://localhost:8000/admin/
echo Username: admin
echo Password: admin123
echo.
pause