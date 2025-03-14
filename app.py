from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session, send_from_directory
from urllib.parse import quote
import os
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.secret_key = 'your-secret-key-here'  # تغيير هذا المفتاح في الإنتاج

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        payment_method = request.form.get('paymentMethod')
        
        # هنا يمكنك إضافة منطق لتخزين البيانات أو إرسال إشعارات
        return jsonify({
            'success': True,
            'message': 'تم استلام طلبك بنجاح! سنتواصل معك قريباً'
        })
    return jsonify({
        'success': False,
        'message': 'حدث خطأ في معالجة الطلب'
    })

# مسار خاص لملفات CSS و JavaScript
@app.route('/static/<path:filename>')
def custom_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
