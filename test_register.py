import requests
import json

# Test data for customer registration
test_customer = {
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": "9876543210"
}

# Test the register endpoint
url = "http://localhost:8000/register/"
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=test_customer, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
except json.JSONDecodeError:
    print(f"Response text: {response.text}")