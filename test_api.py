#!/usr/bin/env python3
"""
Simple script to test the Credit Approval System API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_register_customer():
    """Test customer registration"""
    print("Testing customer registration...")
    url = f"{BASE_URL}/register/"
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "1234567890"
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()['customer_id']
    return None

def test_check_eligibility(customer_id):
    """Test loan eligibility check"""
    print(f"\nTesting loan eligibility for customer {customer_id}...")
    url = f"{BASE_URL}/check-eligibility/"
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 10.5,
        "tenure": 12
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json() if response.status_code == 200 else None

def test_create_loan(customer_id):
    """Test loan creation"""
    print(f"\nTesting loan creation for customer {customer_id}...")
    url = f"{BASE_URL}/create-loan/"
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 10.5,
        "tenure": 12
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()['loan_id']
    return None

def test_view_loan(loan_id):
    """Test viewing loan details"""
    print(f"\nTesting view loan details for loan {loan_id}...")
    url = f"{BASE_URL}/view-loan/{loan_id}/"
    
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def test_view_customer_loans(customer_id):
    """Test viewing customer loans"""
    print(f"\nTesting view customer loans for customer {customer_id}...")
    url = f"{BASE_URL}/view-loans/{customer_id}/"
    
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    """Run all API tests"""
    print("Starting API tests for Credit Approval System")
    print("=" * 50)
    
    try:
        # Test 1: Register customer
        customer_id = test_register_customer()
        if not customer_id:
            print("Failed to register customer. Stopping tests.")
            return
        
        # Test 2: Check eligibility
        eligibility = test_check_eligibility(customer_id)
        if not eligibility:
            print("Failed to check eligibility. Stopping tests.")
            return
        
        # Test 3: Create loan
        loan_id = test_create_loan(customer_id)
        if not loan_id:
            print("Failed to create loan. Continuing with remaining tests.")
        
        # Test 4: View loan details
        if loan_id:
            test_view_loan(loan_id)
        
        # Test 5: View customer loans
        test_view_customer_loans(customer_id)
        
        print("\n" + "=" * 50)
        print("API tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the Django server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()