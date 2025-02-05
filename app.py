from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from urllib.parse import quote
import os
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.secret_key = 'your-secret-key-here'  # تغيير هذا المفتاح في الإنتاج

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        # Here you can add logic to store the data or send notifications
        flash('شكراً لتسجيلك! سنتواصل معك قريباً', 'success')
        return redirect(url_for('confirmation'))
    return render_template('confirmation.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '3762':
            session['logged_in'] = True
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('services'))
        else:
            flash('كلمة المرور غير صحيحة', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/course-details')
def course_details():
    return render_template('course_details.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
