# ============================================================
# Gym & Fitness Management System
# app.py — Main Flask Application
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from datetime import date

app = Flask(__name__)
app.secret_key = 'gym_secret_key_2025'

# ============================================================
# Database Connection
# ============================================================
def get_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',         # change to your MySQL username
        password='',         # change to your MySQL password
        database='gym_db'
    )

# ============================================================
# HOME — Summary Dashboard
# Uses COUNT, AVG aggregate functions
# ============================================================
@app.route('/')
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Total members
    cursor.execute("SELECT COUNT(*) AS total FROM members")
    total_members = cursor.fetchone()['total']

    # Total trainers
    cursor.execute("SELECT COUNT(*) AS total FROM trainers")
    total_trainers = cursor.fetchone()['total']

    # Total classes
    cursor.execute("SELECT COUNT(*) AS total FROM classes")
    total_classes = cursor.fetchone()['total']

    # Average membership duration (calculated dynamically - 3NF)
    cursor.execute("""
        SELECT ROUND(AVG(DATEDIFF(membership_end_date, membership_start_date)), 1)
        AS avg_duration FROM members
    """)
    avg_duration = cursor.fetchone()['avg_duration']

    # Most popular class
    cursor.execute("""
        SELECT c.class_name, COUNT(e.enrollment_id) AS total
        FROM classes c
        JOIN class_enrollments e ON c.class_id = e.class_id
        GROUP BY c.class_id, c.class_name
        ORDER BY total DESC LIMIT 1
    """)
    popular_class = cursor.fetchone()

    # Membership type breakdown
    cursor.execute("""
        SELECT membership_type, COUNT(*) AS total
        FROM members GROUP BY membership_type
    """)
    membership_breakdown = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('dashboard.html',
        total_members=total_members,
        total_trainers=total_trainers,
        total_classes=total_classes,
        avg_duration=avg_duration,
        popular_class=popular_class,
        membership_breakdown=membership_breakdown
    )

# ============================================================
# MEMBERS — List all members
# ============================================================
@app.route('/members')
def members():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.*, t.first_name AS trainer_first, t.last_name AS trainer_last,
               DATEDIFF(m.membership_end_date, m.membership_start_date) AS duration_days
        FROM members m
        LEFT JOIN trainers t ON m.trainer_id = t.trainer_id
        ORDER BY m.member_id
    """)
    members = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('members.html', members=members)

# ============================================================
# MEMBERS — Add new member (GET = show form, POST = save)
# Includes server-side data validation
# ============================================================
@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        first_name   = request.form.get('first_name', '').strip()
        last_name    = request.form.get('last_name', '').strip()
        email        = request.form.get('email', '').strip()
        phone        = request.form.get('phone', '').strip()
        dob          = request.form.get('date_of_birth', '').strip()
        m_type       = request.form.get('membership_type', '').strip()
        start_date   = request.form.get('membership_start_date', '').strip()
        end_date     = request.form.get('membership_end_date', '').strip()
        trainer_id   = request.form.get('trainer_id') or None

        # --- Server-side Validation ---
        errors = []
        if not first_name:  errors.append('First name is required.')
        if not last_name:   errors.append('Last name is required.')
        if not email:       errors.append('Email is required.')
        if '@' not in email: errors.append('Email must be valid.')
        if not dob:         errors.append('Date of birth is required.')
        if not start_date:  errors.append('Membership start date is required.')
        if not end_date:    errors.append('Membership end date is required.')
        if start_date and end_date and end_date <= start_date:
            errors.append('End date must be after start date.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            cursor.execute("SELECT * FROM trainers ORDER BY first_name")
            trainers = cursor.fetchall()
            cursor.close()
            db.close()
            return render_template('member_form.html', trainers=trainers, action='Add')

        try:
            cursor.execute("""
                INSERT INTO members
                (first_name, last_name, email, phone, date_of_birth,
                 membership_type, membership_start_date, membership_end_date, trainer_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, email, phone, dob,
                  m_type, start_date, end_date, trainer_id))
            db.commit()
            flash('Member added successfully!', 'success')
            return redirect(url_for('members'))
        except Error as e:
            db.rollback()
            flash(f'Database error: {e}', 'danger')

    cursor.execute("SELECT * FROM trainers ORDER BY first_name")
    trainers = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('member_form.html', trainers=trainers, action='Add')

# ============================================================
# MEMBERS — Edit member
# ============================================================
@app.route('/members/edit/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        first_name   = request.form.get('first_name', '').strip()
        last_name    = request.form.get('last_name', '').strip()
        email        = request.form.get('email', '').strip()
        phone        = request.form.get('phone', '').strip()
        dob          = request.form.get('date_of_birth', '').strip()
        m_type       = request.form.get('membership_type', '').strip()
        start_date   = request.form.get('membership_start_date', '').strip()
        end_date     = request.form.get('membership_end_date', '').strip()
        trainer_id   = request.form.get('trainer_id') or None

        # --- Validation ---
        errors = []
        if not first_name: errors.append('First name is required.')
        if not last_name:  errors.append('Last name is required.')
        if not email:      errors.append('Email is required.')
        if start_date and end_date and end_date <= start_date:
            errors.append('End date must be after start date.')

        if errors:
            for e in errors:
                flash(e, 'danger')
        else:
            try:
                cursor.execute("""
                    UPDATE members SET first_name=%s, last_name=%s, email=%s, phone=%s,
                    date_of_birth=%s, membership_type=%s, membership_start_date=%s,
                    membership_end_date=%s, trainer_id=%s
                    WHERE member_id=%s
                """, (first_name, last_name, email, phone, dob,
                      m_type, start_date, end_date, trainer_id, member_id))
                db.commit()
                flash('Member updated successfully!', 'success')
                return redirect(url_for('members'))
            except Error as e:
                db.rollback()
                flash(f'Database error: {e}', 'danger')

    cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    member = cursor.fetchone()
    cursor.execute("SELECT * FROM trainers ORDER BY first_name")
    trainers = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('member_form.html', member=member, trainers=trainers, action='Edit')

# ============================================================
# MEMBERS — Delete member
# ============================================================
@app.route('/members/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM class_enrollments WHERE member_id = %s", (member_id,))
        cursor.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
        db.commit()
        flash('Member deleted.', 'success')
    except Error as e:
        db.rollback()
        flash(f'Error: {e}', 'danger')
    cursor.close()
    db.close()
    return redirect(url_for('members'))

# ============================================================
# CLASSES — List all classes
# ============================================================
@app.route('/classes')
def classes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, t.first_name AS trainer_first, t.last_name AS trainer_last,
               COUNT(e.enrollment_id) AS enrolled
        FROM classes c
        JOIN trainers t ON c.trainer_id = t.trainer_id
        LEFT JOIN class_enrollments e ON c.class_id = e.class_id
        GROUP BY c.class_id
        ORDER BY c.class_date, c.start_time
    """)
    classes = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('classes.html', classes=classes)

# ============================================================
# CLASSES — Add new class
# ============================================================
@app.route('/classes/add', methods=['GET', 'POST'])
def add_class():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        class_name    = request.form.get('class_name', '').strip()
        trainer_id    = request.form.get('trainer_id', '').strip()
        class_date    = request.form.get('class_date', '').strip()
        start_time    = request.form.get('start_time', '').strip()
        duration_mins = request.form.get('duration_mins', '').strip()
        max_capacity  = request.form.get('max_capacity', '').strip()
        room          = request.form.get('room', '').strip()

        # --- Validation ---
        errors = []
        if not class_name:    errors.append('Class name is required.')
        if not trainer_id:    errors.append('Trainer is required.')
        if not class_date:    errors.append('Class date is required.')
        if not start_time:    errors.append('Start time is required.')
        if not duration_mins or int(duration_mins) <= 0:
            errors.append('Duration must be a positive number.')
        if not max_capacity or int(max_capacity) <= 0:
            errors.append('Max capacity must be a positive number.')

        if errors:
            for e in errors:
                flash(e, 'danger')
        else:
            try:
                cursor.execute("""
                    INSERT INTO classes
                    (class_name, trainer_id, class_date, start_time, duration_mins, max_capacity, room)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (class_name, trainer_id, class_date, start_time,
                      duration_mins, max_capacity, room))
                db.commit()
                flash('Class added successfully!', 'success')
                return redirect(url_for('classes'))
            except Error as e:
                db.rollback()
                flash(f'Database error: {e}', 'danger')

    cursor.execute("SELECT * FROM trainers ORDER BY first_name")
    trainers = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('class_form.html', trainers=trainers, action='Add')

# ============================================================
# CLASSES — Delete class
# ============================================================
@app.route('/classes/delete/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM class_enrollments WHERE class_id = %s", (class_id,))
        cursor.execute("DELETE FROM classes WHERE class_id = %s", (class_id,))
        db.commit()
        flash('Class deleted.', 'success')
    except Error as e:
        db.rollback()
        flash(f'Error: {e}', 'danger')
    cursor.close()
    db.close()
    return redirect(url_for('classes'))

# ============================================================
# ENROLLMENTS — View all enrollments (Relationship Management)
# Shows One-to-Many: members → class_enrollments ← classes
# ============================================================
@app.route('/enrollments')
def enrollments():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.enrollment_id, e.attendance, e.enrolled_at,
               m.first_name AS member_first, m.last_name AS member_last,
               m.membership_type,
               c.class_name, c.class_date, c.start_time,
               t.first_name AS trainer_first, t.last_name AS trainer_last
        FROM class_enrollments e
        JOIN members m ON e.member_id = m.member_id
        JOIN classes c ON e.class_id = c.class_id
        JOIN trainers t ON c.trainer_id = t.trainer_id
        ORDER BY c.class_date, c.start_time
    """)
    enrollments = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('enrollments.html', enrollments=enrollments)

# ============================================================
# ENROLLMENTS — Enroll a member in a class
# TRANSACTION LOGIC: checks capacity before enrolling
# If class is full, the enrollment is rolled back
# ============================================================
@app.route('/enrollments/add', methods=['GET', 'POST'])
def add_enrollment():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        member_id  = request.form.get('member_id')
        class_id   = request.form.get('class_id')
        attendance = request.form.get('attendance', 'registered')

        # --- Validation ---
        if not member_id or not class_id:
            flash('Please select both a member and a class.', 'danger')
        else:
            try:
                # --- TRANSACTION START ---
                # Step 1: Check current enrollment count vs max capacity
                cursor.execute("""
                    SELECT c.max_capacity,
                           COUNT(e.enrollment_id) AS current_enrolled
                    FROM classes c
                    LEFT JOIN class_enrollments e ON c.class_id = e.class_id
                    WHERE c.class_id = %s
                    GROUP BY c.class_id, c.max_capacity
                """, (class_id,))
                result = cursor.fetchone()

                if result and result['current_enrolled'] >= result['max_capacity']:
                    # Capacity full — do NOT enroll, rollback
                    flash('Class is full! Enrollment not added.', 'warning')
                else:
                    # Step 2: Check if already enrolled
                    cursor.execute("""
                        SELECT * FROM class_enrollments
                        WHERE member_id = %s AND class_id = %s
                    """, (member_id, class_id))
                    existing = cursor.fetchone()

                    if existing:
                        flash('Member is already enrolled in this class.', 'warning')
                    else:
                        # Step 3: Insert enrollment record
                        cursor.execute("""
                            INSERT INTO class_enrollments (member_id, class_id, attendance)
                            VALUES (%s, %s, %s)
                        """, (member_id, class_id, attendance))
                        db.commit()
                        # --- TRANSACTION END ---
                        flash('Member enrolled successfully!', 'success')
                        return redirect(url_for('enrollments'))

            except Error as e:
                db.rollback()
                flash(f'Transaction failed: {e}', 'danger')

    cursor.execute("SELECT * FROM members ORDER BY first_name")
    members = cursor.fetchall()
    cursor.execute("""
        SELECT c.*, t.first_name AS trainer_first, t.last_name AS trainer_last
        FROM classes c JOIN trainers t ON c.trainer_id = t.trainer_id
        ORDER BY c.class_date
    """)
    classes = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('enrollment_form.html', members=members, classes=classes)

# ============================================================
# ENROLLMENTS — Delete enrollment
# ============================================================
@app.route('/enrollments/delete/<int:enrollment_id>', methods=['POST'])
def delete_enrollment(enrollment_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM class_enrollments WHERE enrollment_id = %s", (enrollment_id,))
        db.commit()
        flash('Enrollment removed.', 'success')
    except Error as e:
        db.rollback()
        flash(f'Error: {e}', 'danger')
    cursor.close()
    db.close()
    return redirect(url_for('enrollments'))

# ============================================================
# TRAINERS — List all trainers
# ============================================================
@app.route('/trainers')
def trainers():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, COUNT(m.member_id) AS total_members
        FROM trainers t
        LEFT JOIN members m ON t.trainer_id = m.trainer_id
        GROUP BY t.trainer_id
        ORDER BY t.first_name
    """)
    trainers = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('trainers.html', trainers=trainers)

if __name__ == '__main__':
    app.run(debug=True)
