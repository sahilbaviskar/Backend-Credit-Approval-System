import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    print("=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_register():
    print("=== Testing Customer Registration ===")
    customer_data = {
        "first_name": "Test",
        "last_name": "Customer",
        "age": 35,
        "monthly_income": 60000,
        "phone_number": "9999999999"
    }
    
    response = requests.post(f"{BASE_URL}/register/", json=customer_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print()
    return result.get('customer_id')

def test_check_eligibility(customer_id):
    print("=== Testing Loan Eligibility Check ===")
    eligibility_data = {
        "customer_id": customer_id,
        "loan_amount": 500000,
        "interest_rate": 12.0,
        "tenure": 24
    }
    
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=eligibility_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_loan(customer_id):
    print("=== Testing Loan Creation ===")
    loan_data = {
        "customer_id": customer_id,
        "loan_amount": 300000,
        "interest_rate": 10.0,
        "tenure": 12
    }
    
    response = requests.post(f"{BASE_URL}/create-loan/", json=loan_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    print()
    return result.get('loan_id')

def test_view_loan(loan_id):
    if loan_id:
        print("=== Testing View Loan ===")
        response = requests.get(f"{BASE_URL}/view-loan/{loan_id}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()

def test_view_customer_loans(customer_id):
    print("=== Testing View Customer Loans ===")
    response = requests.get(f"{BASE_URL}/view-loans/{customer_id}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    print("Testing Credit Approval System API Endpoints")
    print("=" * 50)
    
    # Test all endpoints
    test_health_check()
    customer_id = test_register()
    
    if customer_id:
        test_check_eligibility(customer_id)
        loan_id = test_create_loan(customer_id)
        test_view_loan(loan_id)
        test_view_customer_loans(customer_id)
    
    print("All tests completed!")