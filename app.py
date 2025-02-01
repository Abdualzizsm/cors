from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from urllib.parse import quote
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

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

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    phone = request.form.get('phone')
    
    # تنسيق رقم الهاتف
    if phone.startswith('0'):
        phone = '966' + phone[1:]
    
    # إنشاء رابط الواتساب
    message = f"مرحباً، أنا {name} وأرغب في الاستفسار عن كورس البرمجة"
    whatsapp_url = f"https://wa.me/{phone}?text={quote(message)}"
    
    return jsonify({
        'success': True,
        'whatsapp_url': whatsapp_url
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
