from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, make_response, session
import os
import logging
from datetime import datetime
import secrets
import sqlite3
import hashlib
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            static_folder='static',  # استخدام المجلد القياسي للملفات الاستاتيكية
            template_folder='templates')  # استخدام المجلد القياسي للقوالب
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.secret_key = secrets.token_hex(16)

# إنشاء قاعدة البيانات للإحصائيات
def init_db():
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    # جدول الزيارات
    c.execute('''
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page TEXT NOT NULL,
        ip TEXT,
        user_agent TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        session_id TEXT
    )
    ''')
    conn.commit()
    conn.close()

# تأكد من إنشاء قاعدة البيانات عند بدء التطبيق
init_db()

# دالة لتسجيل الزيارات
def log_visit(page):
    if request.path.startswith('/static/') or request.path.startswith('/admin'):
        return
    
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    
    ip = request.remote_addr
    user_agent = request.user_agent.string
    session_id = session.get('session_id', '')
    
    if not session_id:
        session_id = secrets.token_hex(8)
        session['session_id'] = session_id
    
    c.execute("INSERT INTO visits (page, ip, user_agent, session_id) VALUES (?, ?, ?, ?)",
              (page, ip, user_agent, session_id))
    conn.commit()
    conn.close()

# دالة التحقق من كلمة المرور
def check_password(password):
    # استخدام التجزئة لأمان أفضل (لا تخزن كلمة المرور في الكود بشكل مباشر)
    correct_hash = "4b8373d016f277527198385ba72fda0feb5da015da804e7c068f67948c25205b"  # تجزئة لكلمة المرور 3762
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password == correct_hash

@app.before_request
def before_request():
    # تسجيل الزيارات لجميع الصفحات
    log_visit(request.path)

# مسار للصفحة الرئيسية
@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

# مسارات تحسين محركات البحث
@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    """تقديم ملف sitemap.xml من مجلد static لكن مع جعله متاحًا في جذر الموقع"""
    response = make_response(send_from_directory('static', 'sitemap.xml'))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/manifest.json')
def manifest():
    """تقديم ملف manifest.json من مجلد static لكن مع جعله متاحًا في جذر الموقع"""
    response = make_response(send_from_directory('static', 'manifest.json'))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/favicon.ico')
def favicon():
    """تقديم ملف favicon.ico من مجلد static"""
    return send_from_directory('static', 'favicon.ico')

@app.route('/google-verification')
def google_verification():
    """صفحة التحقق من ملكية الموقع على Google Search Console"""
    return render_template('google-verification.html')

# مسار التحقق من Google للنطاق الجديد
@app.route('/.well-known/acme-challenge/<token>')
def acme_challenge(token):
    """مسار للتحقق من ملكية النطاق أثناء إعداد SSL"""
    return token

# إعادة توجيه URLs غير الصالحة إلى الصفحة الرئيسية
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    """Handle registration form submissions."""
    if request.method == 'POST':
        try:
            # Extract form data
            data = request.get_json()
            
            # Log registration attempt
            logger.info(f"Registration attempt: {data['email']}")
            
            # Here you would add logic to store data or send notifications
            # For example, saving to a database or sending an email
            
            return jsonify({
                'success': True,
                'message': 'تم استلام طلبك بنجاح! سنتواصل معك قريباً'
            })
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'حدث خطأ في معالجة الطلب'
            }), 500
    
    return jsonify({
        'success': False,
        'message': 'طريقة الطلب غير مدعومة'
    }), 405

@app.route('/static/<path:filename>')
def custom_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_password(password):
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'كلمة المرور غير صحيحة'
    
    # التحقق إذا كان المستخدم قد سجل الدخول بالفعل
    if session.get('admin'):
        return redirect(url_for('dashboard'))
    
    return render_template('admin_login.html', error=error)

@app.route('/admin/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    # استخراج إحصائيات من قاعدة البيانات
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    
    # إجمالي الزيارات
    c.execute("SELECT COUNT(*) FROM visits")
    total_visits = c.fetchone()[0]
    
    # الزوار الفريدين (اعتمادًا على session_id)
    c.execute("SELECT COUNT(DISTINCT session_id) FROM visits")
    unique_visitors = c.fetchone()[0]
    
    # أكثر الصفحات زيارة
    c.execute("""
    SELECT page, COUNT(*) as count 
    FROM visits 
    GROUP BY page 
    ORDER BY count DESC 
    LIMIT 10
    """)
    top_pages = c.fetchall()
    
    # الزيارات على مدار الأيام الماضية (7 أيام)
    c.execute("""
    SELECT DATE(timestamp) as date, COUNT(*) as count 
    FROM visits 
    WHERE timestamp > date('now', '-7 days') 
    GROUP BY date 
    ORDER BY date
    """)
    visits_per_day = c.fetchall()
    
    conn.close()
    
    # تحويل البيانات إلى تنسيق مناسب للرسوم البيانية
    days = [day for day, _ in visits_per_day]
    counts = [count for _, count in visits_per_day]
    
    return render_template('dashboard.html', 
                          total_visits=total_visits,
                          unique_visitors=unique_visitors,
                          top_pages=top_pages,
                          days=json.dumps(days),
                          counts=json.dumps(counts))

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/data')
def admin_data():
    if not session.get('admin'):
        return jsonify({"error": "غير مصرح"}), 401
    
    # استخراج إحصائيات إضافية
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    
    # الزيارات بحسب المتصفح
    c.execute("""
    SELECT 
        CASE 
            WHEN user_agent LIKE '%Chrome%' THEN 'Chrome'
            WHEN user_agent LIKE '%Firefox%' THEN 'Firefox'
            WHEN user_agent LIKE '%Safari%' THEN 'Safari'
            WHEN user_agent LIKE '%Edge%' THEN 'Edge'
            ELSE 'Other'
        END as browser,
        COUNT(*) as count
    FROM visits
    GROUP BY browser
    ORDER BY count DESC
    """)
    browsers = c.fetchall()
    
    conn.close()
    
    return jsonify({
        "browsers": {browser: count for browser, count in browsers}
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
