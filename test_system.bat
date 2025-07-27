@echo off
echo Testing Credit Approval System APIs...
echo.

echo Testing health check...
curl -X GET http://localhost:8000/health/
echo.
echo.

echo Testing customer registration...
curl -X POST http://localhost:8000/register/ -H "Content-Type: application/json" -d "{\"first_name\": \"John\", \"last_name\": \"Doe\", \"age\": 30, \"monthly_income\": 50000, \"phone_number\": \"1234567890\"}"
echo.
echo.

echo Testing loan eligibility...
curl -X POST http://localhost:8000/check-eligibility/ -H "Content-Type: application/json" -d "{\"customer_id\": 1, \"loan_amount\": 100000, \"interest_rate\": 10.5, \"tenure\": 12}"
echo.
echo.

pause