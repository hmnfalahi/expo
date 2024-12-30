# Expense Tracker

A Django application for tracking shared expenses among groups of people.

## Features

- User authentication
- Create and manage expense groups
- Add expenses with custom split options
- Automatic balance calculation
- Responsive Bootstrap UI

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Usage

1. Log in to the admin interface at `/admin`
2. Create some users through the admin interface
3. Users can then:
   - Create expense groups
   - Add other users to groups
   - Add expenses with custom splits
   - View balances and settlements

## Testing

Run the tests with:
```bash
python manage.py test
```