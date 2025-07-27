# Credit Approval System

A Django-based credit approval system that evaluates loan applications based on historical data and customer credit scores.

## Features

- Customer registration with automatic credit limit calculation
- Credit score calculation based on historical loan data
- Loan eligibility checking with dynamic interest rate correction
- Loan creation and management
- Background data ingestion using Celery
- RESTful API endpoints
- Dockerized application with PostgreSQL and Redis

## Tech Stack

- **Backend**: Django 4.2.7, Django REST Framework
- **Database**: PostgreSQL
- **Cache/Message Broker**: Redis
- **Background Tasks**: Celery
- **Containerization**: Docker, Docker Compose
- **Data Processing**: Pandas, OpenPyXL

## API Endpoints

### 1. Register Customer
- **URL**: `POST /register/`
- **Description**: Add a new customer with auto-calculated approved limit
- **Request Body**:
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": "1234567890"
}
```
- **Response**:
```json
{
    "customer_id": 1,
    "name": "John Doe",
    "age": 30,
    "monthly_income": 50000,
    "approved_limit": 1800000,
    "phone_number": "1234567890"
}
```

### 2. Check Loan Eligibility
- **URL**: `POST /check-eligibility/`
- **Description**: Check if a customer is eligible for a loan
- **Request Body**:
```json
{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 10.5,
    "tenure": 12
}
```
- **Response**:
```json
{
    "customer_id": 1,
    "approval": true,
    "interest_rate": 10.5,
    "corrected_interest_rate": 12.0,
    "tenure": 12,
    "monthly_installment": 8884.88
}
```

### 3. Create Loan
- **URL**: `POST /create-loan/`
- **Description**: Create a new loan if eligible
- **Request Body**:
```json
{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 10.5,
    "tenure": 12
}
```
- **Response**:
```json
{
    "loan_id": 1,
    "customer_id": 1,
    "loan_approved": true,
    "message": "Loan approved successfully",
    "monthly_installment": 8884.88
}
```

### 4. View Loan Details
- **URL**: `GET /view-loan/{loan_id}/`
- **Description**: Get details of a specific loan
- **Response**:
```json
{
    "loan_id": 1,
    "customer": {
        "customer_id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "1234567890",
        "age": 30
    },
    "loan_amount": 100000,
    "interest_rate": 12.0,
    "monthly_repayment": 8884.88,
    "tenure": 12,
    "repayments_left": 12
}
```

### 5. View Customer Loans
- **URL**: `GET /view-loans/{customer_id}/`
- **Description**: Get all active loans for a customer
- **Response**:
```json
[
    {
        "loan_id": 1,
        "loan_amount": 100000,
        "interest_rate": 12.0,
        "monthly_repayment": 8884.88,
        "repayments_left": 12
    }
]
```

## Credit Score Calculation

The system calculates credit scores (0-100) based on:

1. **Past Loans Paid on Time** (40% weight)
2. **Number of Loans Taken** (20% weight)
3. **Loan Activity in Current Year** (20% weight)
4. **Loan Volume vs Approved Limit** (20% weight)

### Approval Rules

- **Credit Score > 50**: Approve loan with any interest rate
- **30 < Credit Score ≤ 50**: Approve with minimum 12% interest rate
- **10 < Credit Score ≤ 30**: Approve with minimum 16% interest rate
- **Credit Score ≤ 10**: Reject loan
- **Total EMIs > 50% of salary**: Reject loan
- **Current loans > approved limit**: Credit score = 0

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start

1. **Clone the repository**:
```bash
git clone <repository-url>
cd BackendInternship
```

2. **Start the application**:
```bash
docker-compose up --build
```

3. **Run migrations** (in a new terminal):
```bash
docker-compose exec web python manage.py migrate
```

4. **Ingest initial data**:
```bash
docker-compose exec web python manage.py ingest_data
```

5. **Create superuser** (optional):
```bash
docker-compose exec web python manage.py createsuperuser
```

The application will be available at `http://localhost:8000`

### Manual Setup (without Docker)

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your database and Redis URLs
```

3. **Run migrations**:
```bash
python manage.py migrate
```

4. **Start Redis and PostgreSQL** (ensure they're running)

5. **Start Celery worker**:
```bash
celery -A credit_approval worker --loglevel=info
```

6. **Start Django server**:
```bash
python manage.py runserver
```

7. **Ingest data**:
```bash
python manage.py ingest_data
```

## Data Files

The system expects two Excel files in the project root:

- `customer_data.xlsx`: Customer information
- `loan_data.xlsx`: Historical loan data

These files are automatically processed during the data ingestion step.

## Testing

Run the test suite:

```bash
# With Docker
docker-compose exec web python manage.py test

# Without Docker
python manage.py test
```

## Project Structure

```
BackendInternship/
├── credit_approval/          # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── loans/                    # Main application
│   ├── models.py            # Customer and Loan models
│   ├── views.py             # API endpoints
│   ├── serializers.py       # DRF serializers
│   ├── utils.py             # Credit score calculation
│   ├── tasks.py             # Celery tasks
│   ├── urls.py              # URL routing
│   ├── admin.py             # Django admin
│   ├── tests.py             # Unit tests
│   └── management/
│       └── commands/
│           └── ingest_data.py
├── customer_data.xlsx        # Customer data file
├── loan_data.xlsx           # Loan data file
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── manage.py               # Django management script
└── README.md               # This file
```

## Environment Variables

- `DEBUG`: Enable/disable debug mode
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## API Testing

You can test the APIs using tools like Postman, curl, or any HTTP client. Here are some example curl commands:

### Register a customer:
```bash
curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": "1234567890"
  }'
```

### Check eligibility:
```bash
curl -X POST http://localhost:8000/check-eligibility/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 10.5,
    "tenure": 12
  }'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.