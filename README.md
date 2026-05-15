# GymFit Management System

A full-stack web application for managing a gym's members, trainers, classes, and enrollments. Built with Python (Flask), MySQL, and Bootstrap.

---

## Project Description

GymFit is a gym management system that allows staff to:
- Manage member profiles and membership details
- Schedule and manage fitness classes
- Enroll members in classes with automatic capacity checking
- View trainers and their assigned members
- Monitor key metrics on a summary dashboard

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Database | MySQL |
| DB Driver | mysql-connector-python |
| Frontend | HTML5, Bootstrap 5, Jinja2 |
| Version Control | Git |

---

## Installation Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/gym-fitness-app.git
cd gym-fitness-app
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install flask mysql-connector-python
```

### 4. Configure database credentials
Open `app.py` and update the `get_db()` function:
```python
def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',       # your MySQL username
        password='',       # your MySQL password
        database='gym_db'
    )
```

---

## Database Setup

### Run the schema script in MySQL:
```bash
mysql -u root -p < schema.sql
```
Or open `schema.sql` in MySQL Workbench and run it. This will create the `gym_db` database, all tables, and insert sample data.

---

## Usage

### Start the Flask server:
```bash
python3 app.py
```

### Open your browser and go to:
```
http://127.0.0.1:5000
```

### Navigation:
| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Summary stats and metrics |
| Members | `/members` | View, add, edit, delete members |
| Classes | `/classes` | View and manage fitness classes |
| Enrollments | `/enrollments` | Manage member-class enrollments |
| Trainers | `/trainers` | View trainer profiles |

---

## Key Features

- **Multi-Table CRUD** — Full create/read/update/delete for members and classes
- **Relationship Display** — Enrollments page shows the full member → class → trainer relationship
- **Transaction Logic** — Enrollment checks class capacity before inserting; rolls back if full
- **Data Validation** — Server-side validation on all forms (required fields, date logic, positive numbers)
- **Summary Dashboard** — Uses COUNT, AVG SQL aggregates to display live gym metrics
# Gym Fitness App
