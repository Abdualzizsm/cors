from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, make_response, session
import os
import logging
from datetime import datetime
import secrets
import sqlite3
import hashlib
import json
import ipaddress

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# تحميل المكتبات الاختيارية مع التعامل مع حالة عدم وجودها
try:
    from user_agents import parse
    USER_AGENTS_AVAILABLE = True
except ImportError:
    USER_AGENTS_AVAILABLE = False

try:
    import geoip2.database
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False

app = Flask(__name__, 
            static_folder='static',  # استخدام المجلد القياسي للملفات الاستاتيكية
            template_folder='templates')  # استخدام المجلد القياسي للقوالب
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.secret_key = secrets.token_hex(16)

# دالة لإعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    # جدول الزيارات
    c.execute('''
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page TEXT,
        ip TEXT,
        user_agent TEXT,
        session_id TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        referrer TEXT,
        country TEXT,
        city TEXT,
        browser TEXT,
        os TEXT,
        device TEXT
    )
    ''')
    
    # التحقق من وجود بيانات تجريبية للعرض
    c.execute("SELECT COUNT(*) FROM visits")
    count = c.fetchone()[0]
    
    # إذا كانت قاعدة البيانات فارغة، أضف بعض البيانات التجريبية
    if count == 0:
        sample_browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
        sample_os = ['Windows', 'MacOS', 'iOS', 'Android', 'Linux']
        sample_devices = ['Desktop', 'Mobile', 'Tablet']
        sample_pages = ['/', '/contact', '/about', '/products', '/services']
        sample_countries = ['المملكة العربية السعودية', 'الإمارات', 'مصر', 'الكويت', 'قطر']
        
        for i in range(30):
            browser = sample_browsers[i % len(sample_browsers)]
            os_name = sample_os[i % len(sample_os)]
            device = sample_devices[i % len(sample_devices)]
            page = sample_pages[i % len(sample_pages)]
            country = sample_countries[i % len(sample_countries)]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # إضافة بيانات عشوائية للتجربة
            c.execute('''
                INSERT INTO visits 
                (page, ip, user_agent, session_id, timestamp, referrer, country, city, browser, os, device) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', 
                (page, f"192.168.1.{i+1}", "Mozilla/5.0", f"session_{i}", timestamp, 
                "https://google.com", country, "المدينة", browser, os_name, device)
            )
    
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
    user_agent_string = request.user_agent.string
    session_id = session.get('session_id', '')
    referrer = request.referrer or ''
    
    # استخلاص معلومات المتصفح ونظام التشغيل والجهاز
    if USER_AGENTS_AVAILABLE:
        user_agent = parse(user_agent_string)
        browser = user_agent.browser.family
        os = user_agent.os.family
        device = "Mobile" if user_agent.is_mobile else ("Tablet" if user_agent.is_tablet else "Desktop")
    else:
        browser = "غير معروف"
        os = "غير معروف"
        device = "غير معروف"
    
    # استخلاص معلومات الموقع الجغرافي
    country = "غير معروف"
    city = "غير معروف"
    
    if GEOIP_AVAILABLE:
        try:
            # في الإنتاج، يمكنك استخدام خدمة MaxMind GeoIP مع مفتاح API
            reader = geoip2.database.Reader('GeoLite2-City.mmdb')
            response = reader.city(ip)
            country = response.country.name or "غير معروف"
            city = response.city.name or "غير معروف"
            reader.close()
        except Exception as e:
            logger.error(f"خطأ في استخلاص المعلومات الجغرافية: {str(e)}")
    
    # التحقق من وجود الجدول وإنشاؤه إذا لم يكن موجودًا
    c.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page TEXT,
            ip TEXT,
            user_agent TEXT,
            session_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            referrer TEXT,
            country TEXT,
            city TEXT,
            browser TEXT,
            os TEXT,
            device TEXT
        )
    ''')
    
    # إضافة معلومات الزيارة
    c.execute('''
        INSERT INTO visits (page, ip, user_agent, session_id, referrer, country, city, browser, os, device)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (page, ip, user_agent_string, session_id, referrer, country, city, browser, os, device))
    
    conn.commit()
    conn.close()

# دالة التحقق من كلمة المرور
def check_password(password):
    # التحقق المباشر من كلمة المرور (3762)
    return password == '3762'

@app.before_request
def before_request():
    # إنشاء معرف جلسة للزائر إذا لم يكن موجودًا
    if 'session_id' not in session:
        session['session_id'] = str(secrets.token_hex(16))
    
    # استثناء الملفات الثابتة والصور والصفحات الإدارية من التتبع
    if not request.path.startswith('/static') and not request.path.startswith('/admin') and request.method == 'GET':
        log_visit(request.path)

# مسار للصفحة الرئيسية (صفحة الذكاء الاصطناعي)
@app.route('/')
def index():
    log_visit('ai_community')
    return render_template('ai_community.html')

# مسار لصفحة أدوات الكتابة
@app.route('/writing-tools')
def writing_tools():
    log_visit('writing_tools')
    return render_template('writing_tools.html')

# مسار لصفحة أدوات إنشاء الصور
@app.route('/image-generation')
def image_generation():
    log_visit('image_generation')
    return render_template('image_generation.html')

# مسار لصفحة أدوات إنشاء الفيديو
@app.route('/video-creation')
def video_creation():
    log_visit('video_creation')
    return render_template('video_creation.html')

# مسار لصفحة المقاطع الصوتية
@app.route('/audio-clips')
def audio_clips():
    log_visit('audio_clips')
    return render_template('audio_clips.html')

# مسار لصفحة مكتبة النصوص الإرشادية
@app.route('/prompt-library')
def prompt_library():
    log_visit('prompt_library')
    return render_template('prompt_library.html')

# مسار لصفحة منتدى المناقشة
@app.route('/discussion-forum')
def discussion_forum():
    log_visit('discussion_forum')
    return render_template('discussion_forum.html')

# مسار لصفحة الانضمام المدفوعة (الصفحة الرئيسية القديمة)
@app.route('/join')
def join():
    log_visit('join')
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
    
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    
    # الحصول على إحصائيات الزيارات خلال الـ 7 أيام الماضية
    c.execute('''
        SELECT date(timestamp) as day, COUNT(*) as count 
        FROM visits 
        WHERE timestamp >= date('now', '-7 days') 
        GROUP BY day 
        ORDER BY day
    ''')
    
    visits_data = c.fetchall()
    days = [row[0] for row in visits_data]
    counts = [row[1] for row in visits_data]
    
    # الحصول على إحصائيات المتصفحات
    c.execute('''
        SELECT browser, COUNT(*) as count 
        FROM visits 
        GROUP BY browser 
        ORDER BY count DESC
    ''')
    
    browsers_data = c.fetchall()
    browsers = {}
    for row in browsers_data:
        if row[0]:  # تجنب القيم الفارغة
            browsers[row[0]] = row[1]
    
    # الحصول على إحصائيات نظام التشغيل
    c.execute('''
        SELECT os, COUNT(*) as count 
        FROM visits 
        GROUP BY os 
        ORDER BY count DESC
    ''')
    
    os_data = c.fetchall()
    os_stats = {}
    for row in os_data:
        if row[0]:  # تجنب القيم الفارغة
            os_stats[row[0]] = row[1]
    
    # الحصول على إحصائيات الأجهزة
    c.execute('''
        SELECT device, COUNT(*) as count 
        FROM visits 
        GROUP BY device 
        ORDER BY count DESC
    ''')
    
    device_data = c.fetchall()
    device_stats = {}
    for row in device_data:
        if row[0]:  # تجنب القيم الفارغة
            device_stats[row[0]] = row[1]
    
    # الحصول على الصفحات الأكثر زيارة
    c.execute('''
        SELECT page, COUNT(*) as count 
        FROM visits 
        GROUP BY page 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    
    pages_data = c.fetchall()
    
    # الحصول على معلومات آخر 100 زائر مع جميع التفاصيل
    c.execute('''
        SELECT timestamp, ip, country, city, device, browser, os, page, referrer 
        FROM visits 
        ORDER BY timestamp DESC 
        LIMIT 100
    ''')
    
    visitors_info = []
    for row in c.fetchall():
        visitor = {
            'timestamp': row[0],
            'ip': row[1],
            'country': row[2] or 'غير معروف',
            'city': row[3] or 'غير معروف',
            'device': row[4] or 'غير معروف',
            'browser': row[5] or 'غير معروف',
            'os': row[6] or 'غير معروف',
            'page': row[7],
            'referrer': row[8]
        }
        visitors_info.append(visitor)
    
    conn.close()
    
    return render_template('dashboard.html', 
                          days=json.dumps(days), 
                          counts=json.dumps(counts),
                          browsers=json.dumps(browsers),
                          os_stats=json.dumps(os_stats),
                          device_stats=json.dumps(device_stats),
                          pages=pages_data,
                          visitors_info=visitors_info)

@app.route('/admin/data')
def admin_data():
    if not session.get('admin'):
        return jsonify({'error': 'غير مصرح'}), 403
    
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    
    # الحصول على إحصائيات المتصفحات
    c.execute('''
        SELECT browser, COUNT(*) as count 
        FROM visits 
        GROUP BY browser 
        ORDER BY count DESC
    ''')
    
    browsers_data = c.fetchall()
    browsers = {}
    for row in browsers_data:
        if row[0]:  # تجنب القيم الفارغة
            browsers[row[0]] = row[1]
    
    # الحصول على إحصائيات نظام التشغيل
    c.execute('''
        SELECT os, COUNT(*) as count 
        FROM visits 
        GROUP BY os 
        ORDER BY count DESC
    ''')
    
    os_data = c.fetchall()
    os_stats = {}
    for row in os_data:
        if row[0]:  # تجنب القيم الفارغة
            os_stats[row[0]] = row[1]
    
    # الحصول على إحصائيات الأجهزة
    c.execute('''
        SELECT device, COUNT(*) as count 
        FROM visits 
        GROUP BY device 
        ORDER BY count DESC
    ''')
    
    device_data = c.fetchall()
    device_stats = {}
    for row in device_data:
        if row[0]:  # تجنب القيم الفارغة
            device_stats[row[0]] = row[1]
    
    # الحصول على معلومات البلدان
    c.execute('''
        SELECT country, COUNT(*) as count 
        FROM visits 
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country 
        ORDER BY count DESC
    ''')
    
    country_data = c.fetchall()
    countries = {}
    for row in country_data:
        countries[row[0]] = row[1]
    
    conn.close()
    
    return jsonify({
        'browsers': browsers,
        'os': os_stats,
        'devices': device_stats,
        'countries': countries
    })

@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
