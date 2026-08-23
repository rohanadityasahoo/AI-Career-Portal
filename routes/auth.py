from flask import Blueprint, render_template, request
from werkzeug.security import generate_password_hash

from database.db import get_db_connection

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        full_name   = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form.get('password')
        gender = request.form.get('gender')
        college = request.form.get('college')
        branch = request.form.get('branch')
        year = request.form.get('year')
        print(request.form)

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            insert into students
            (full_name,email,phone,password,gender,college,branch,year)
            values (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            full_name,
            email,
            phone,
            hashed_password,
            gender,
            college,
            branch,
            year
        ))

        conn.commit()

        cursor.close()
        conn.close()

        return "Registration Successful"

    return render_template('auth/register.html')

from werkzeug.security import check_password_hash

from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "select * from students where email=%s",
            (email,)
        )

        student = cursor.fetchone()

        cursor.close()
        conn.close()

        if student:

            if check_password_hash(student['password'], password):

                session['student_id'] = student['student_id']
                session['student_name'] = student['full_name']

                return redirect('/dashboard')

        return "Invalid Email or Password"

    return render_template('auth/login.html')

@auth.route('/logout')
def logout():

    session.clear()

    return redirect('/login')