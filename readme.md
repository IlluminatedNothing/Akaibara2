# Akaibara Japanese Surplus POS System

## Requirements
- Python 3.12
- PostgreSQL
- pgAdmin 4

## Setup Instructions

### 1. Clone the repository
git clone https://github.com/yourusername/akaibara-pos.git
cd akaibara-pos

### 2. Create virtual environment
py -3.12 -m venv venv312
venv312\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set up the database
- Open pgAdmin 4
- Create a new database called: pos_database
- Run the SQL script in /sql/schema.sql to create all tables
- Run the SQL script in /sql/sample_data.sql to insert sample data

### 5. Apply Django migrations
python manage.py migrate

### 6. Create a superuser
python manage.py createsuperuser
- Use email: admin@akaibara.com
- Use password: akaibara

### 7. Add sample categories via Django shell
python manage.py shell

from product_catalog.models import Category
Category.objects.create(name='Computers', description='Laptops, desktops, and peripherals')
Category.objects.create(name='Glassware', description='Cups, plates, bowls, and glass items')
Category.objects.create(name='Linens', description='Pillows, bedsheets, and blankets')
Category.objects.create(name='Miscellaneous', description='Random surplus items')
exit()

### 8. Run the server
python manage.py runserver

### 9. Open in browser
http://127.0.0.1:8000/auth/

## Login Credentials
- Email: admin@akaibara.com
- Password: akaibara

## Tech Stack
- Backend: Python 3.12, Django 5.1.1
- Database: PostgreSQL
- Frontend: HTML, CSS, Bootstrap 5
