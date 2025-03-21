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
    
    # جدول المستخدمين
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        avatar_url TEXT,
        is_admin INTEGER DEFAULT 0
    )
    ''')
    
    # جدول الأدوات
    c.execute('''
    CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        website_url TEXT NOT NULL,
        logo_url TEXT,
        pricing TEXT NOT NULL,
        features TEXT NOT NULL,
        usage_steps TEXT NOT NULL,
        added_by INTEGER,
        added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        views_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (added_by) REFERENCES users (id)
    )
    ''')
    
    # جدول المراجعات
    c.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        pros TEXT,
        cons TEXT,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (tool_id) REFERENCES tools (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # جدول الأدوات المحفوظة
    c.execute('''
    CREATE TABLE IF NOT EXISTS saved_tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        tool_id INTEGER NOT NULL,
        saved_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (tool_id) REFERENCES tools (id),
        UNIQUE(user_id, tool_id)
    )
    ''')
    
    # جدول التعليقات
    c.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        parent_id INTEGER,
        FOREIGN KEY (tool_id) REFERENCES tools (id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (parent_id) REFERENCES comments (id)
    )
    ''')
    
    # جدول المناقشات
    c.execute('''
    CREATE TABLE IF NOT EXISTS discussions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        tool_id INTEGER,
        category TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        views_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (tool_id) REFERENCES tools (id)
    )
    ''')
    
    # جدول ردود المناقشات
    c.execute('''
    CREATE TABLE IF NOT EXISTS discussion_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discussion_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (discussion_id) REFERENCES discussions (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
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
    # الحصول على الأدوات المميزة
    conn = sqlite3.connect('analytics.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # الحصول على الأدوات المميزة
    c.execute('''
        SELECT id, name, description, category, logo_url, pricing, 
               website_url, features, views_count
        FROM tools
        WHERE status = 'approved'
        ORDER BY views_count DESC
        LIMIT 6
    ''')
    featured_tools = [dict(row) for row in c.fetchall()]
    
    # الحصول على أحدث الأدوات
    c.execute('''
        SELECT id, name, description, category, logo_url, pricing, 
               website_url, added_date, features
        FROM tools
        WHERE status = 'approved'
        ORDER BY added_date DESC
        LIMIT 8
    ''')
    latest_tools = [dict(row) for row in c.fetchall()]
    
    # معالجة الميزات لعرضها كقائمة
    for tool in featured_tools + latest_tools:
        if 'features' in tool and tool['features']:
            try:
                tool['features_list'] = tool['features'].split('|')[:3]  # أخذ أول 3 ميزات فقط
            except:
                tool['features_list'] = []
    
    # الحصول على إحصائيات الموقع
    c.execute('SELECT COUNT(*) FROM tools WHERE status = "approved"')
    total_tools = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    conn.close()
    
    return render_template('home.html', 
                          featured_tools=featured_tools,
                          latest_tools=latest_tools,
                          stats={
                              'tools': total_tools,
                              'users': total_users
                          })

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

# مسارات الميزات الاجتماعية

# 1. التعليقات
@app.route('/comments/<int:tool_id>', methods=['GET'])
def get_comments(tool_id):
    """الحصول على جميع تعليقات أداة معينة"""
    conn = sqlite3.connect('analytics.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT c.id, c.content, c.created_at, c.parent_id, 
               u.id as user_id, u.username, u.avatar_url
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.tool_id = ?
        ORDER BY c.created_at DESC
    ''', (tool_id,))
    
    comments = [dict(row) for row in c.fetchall()]
    
    # تنظيم التعليقات في تسلسل هرمي (تعليقات وردود)
    parent_comments = []
    comment_replies = {}
    
    for comment in comments:
        if comment['parent_id'] is None:
            parent_comments.append(comment)
        else:
            if comment['parent_id'] not in comment_replies:
                comment_replies[comment['parent_id']] = []
            comment_replies[comment['parent_id']].append(comment)
    
    # إضافة الردود إلى التعليقات الرئيسية
    for comment in parent_comments:
        comment['replies'] = comment_replies.get(comment['id'], [])
    
    conn.close()
    return jsonify(parent_comments)

@app.route('/comments/<int:tool_id>', methods=['POST'])
def add_comment(tool_id):
    """إضافة تعليق جديد على أداة معينة"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    data = request.json
    content = data.get('content')
    parent_id = data.get('parent_id')
    
    if not content or not content.strip():
        return jsonify({'success': False, 'message': 'التعليق لا يمكن أن يكون فارغاً'}), 400
    
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO comments (tool_id, user_id, content, parent_id)
        VALUES (?, ?, ?, ?)
    ''', (tool_id, session['user_id'], content, parent_id))
    
    comment_id = c.lastrowid
    conn.commit()
    
    # الحصول على معلومات المستخدم والتعليق
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT c.id, c.content, c.created_at, c.parent_id, 
               u.id as user_id, u.username, u.avatar_url
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.id = ?
    ''', (comment_id,))
    
    comment = dict(c.fetchone())
    comment['replies'] = []
    
    conn.close()
    return jsonify({'success': True, 'comment': comment})

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """حذف تعليق"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'يجب تسجيل الدخول أولاً'}), 401
    
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    
    # التحقق من أن المستخدم هو صاحب التعليق أو مشرف
    c.execute('''
        SELECT user_id FROM comments WHERE id = ?
    ''', (comment_id,))
    
    result = c.fetchone()
    if not result:
        conn.close()
        return jsonify({'success': False, 'message': 'التعليق غير موجود'}), 404
    
    comment_user_id = result[0]
    
    # التحقق مما إذا كان المستخدم هو المشرف
    c.execute('''
        SELECT is_admin FROM users WHERE id = ?
    ''', (session['user_id'],))
    
    is_admin = c.fetchone()[0]
    
    if session['user_id'] != comment_user_id and not is_admin:
        conn.close()
        return jsonify({'success': False, 'message': 'غير مصرح لك بحذف هذا التعليق'}), 403
    
    # حذف التعليق وجميع الردود عليه
    c.execute('''
        DELETE FROM comments WHERE id = ? OR parent_id = ?
    ''', (comment_id, comment_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# 2. المناقشات
@app.route('/discussions')
def discussions():
    """عرض صفحة المناقشات"""
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'recent')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = sqlite3.connect('analytics.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # بناء استعلام البحث
    query_params = []
    where_clauses = []
    
    if category != 'all':
        where_clauses.append("d.category = ?")
        query_params.append(category)
    
    if search:
        where_clauses.append("(d.title LIKE ? OR d.description LIKE ?)")
        query_params.extend([f'%{search}%', f'%{search}%'])
    
    where_clause = " AND ".join(where_clauses)
    if where_clause:
        where_clause = "WHERE " + where_clause
    
    # تحديد طريقة الترتيب
    order_by = "COALESCE(last_reply_at, d.created_at) DESC"  # الافتراضي: الأحدث
    if sort_by == 'views':
        order_by = "d.views_count DESC"
    elif sort_by == 'rating':
        order_by = "d.created_at DESC"  # يمكن تعديله لاحقاً إذا كان هناك تقييم للمناقشات
    
    # الحصول على إجمالي عدد المناقشات
    c.execute(f'''
        SELECT COUNT(*) as total 
        FROM discussions d 
        {where_clause}
    ''', query_params)
    total = c.fetchone()['total']
    
    # الحصول على المناقشات مع معلومات المستخدم وعدد الردود
    c.execute(f'''
        SELECT d.id, d.title, d.description, d.created_at, d.views_count, d.category,
               u.id as user_id, u.username, u.avatar_url,
               t.id as tool_id, t.name as tool_name,
               COUNT(dr.id) as replies_count,
               (SELECT MAX(created_at) FROM discussion_replies WHERE discussion_id = d.id) as last_reply_at
        FROM discussions d
        JOIN users u ON d.user_id = u.id
        LEFT JOIN tools t ON d.tool_id = t.id
        LEFT JOIN discussion_replies dr ON d.id = dr.discussion_id
        {where_clause}
        GROUP BY d.id
        ORDER BY {order_by}
        LIMIT ? OFFSET ?
    ''', query_params + [per_page, offset])
    
    discussions_list = [dict(row) for row in c.fetchall()]
    
    # الحصول على فئات المناقشات
    c.execute('''
        SELECT category, COUNT(*) as count
        FROM discussions
        GROUP BY category
        ORDER BY count DESC
    ''')
    
    categories = [dict(row) for row in c.fetchall()]
    
    # الحصول على إحصائيات المنتدى
    c.execute('SELECT COUNT(*) FROM discussions')
    total_discussions = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM discussion_replies')
    total_replies = c.fetchone()[0]
    
    c.execute('SELECT COUNT(DISTINCT user_id) FROM discussions')
    total_contributors = c.fetchone()[0]
    
    conn.close()
    
    return render_template('discussions.html', 
                          discussions=discussions_list, 
                          categories=categories,
                          current_category=category,
                          current_search=search,
                          current_sort=sort_by,
                          page=page,
                          total=total,
                          pages=((total - 1) // per_page) + 1,
                          stats={
                              'discussions': total_discussions,
                              'replies': total_replies,
                              'contributors': total_contributors
                          })

@app.route('/discussions/new', methods=['GET', 'POST'])
def new_discussion():
    """إنشاء مناقشة جديدة"""
    if 'user_id' not in session:
        return redirect(url_for('login', next=url_for('new_discussion')))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        tool_id = request.form.get('tool_id') or None
        notifications = 'notifications' in request.form
        
        if not title or not description or not category:
            flash('جميع الحقول المطلوبة يجب ملؤها', 'danger')
            return redirect(url_for('new_discussion'))
        
        conn = sqlite3.connect('analytics.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO discussions (title, description, user_id, tool_id, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, session['user_id'], tool_id, category))
        
        discussion_id = c.lastrowid
        conn.commit()
        conn.close()
        
        flash('تمت إضافة المناقشة بنجاح!', 'success')
        return redirect(url_for('view_discussion', discussion_id=discussion_id))
    
    # الحصول على قائمة الأدوات للاختيار منها
    conn = sqlite3.connect('analytics.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT id, name FROM tools WHERE status = 'approved'
        ORDER BY name
    ''')
    
    tools = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return render_template('new_discussion.html', tools=tools)

@app.route('/discussions/<int:discussion_id>')
def view_discussion(discussion_id):
    """عرض مناقشة معينة وردودها"""
    conn = sqlite3.connect('analytics.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # زيادة عدد المشاهدات
    c.execute('''
        UPDATE discussions SET views_count = views_count + 1 WHERE id = ?
    ''', (discussion_id,))
    conn.commit()
    
    # الحصول على تفاصيل المناقشة
    c.execute('''
        SELECT d.id, d.title, d.description, d.created_at, d.views_count, d.category,
               u.id as user_id, u.username, u.avatar_url,
               t.id as tool_id, t.name as tool_name
        FROM discussions d
        JOIN users u ON d.user_id = u.id
        LEFT JOIN tools t ON d.tool_id = t.id
        WHERE d.id = ?
    ''', (discussion_id,))
    
    discussion = c.fetchone()
    if not discussion:
        conn.close()
        flash('المناقشة غير موجودة', 'danger')
        return redirect(url_for('discussions'))
    
    discussion = dict(discussion)
    
    # الحصول على الردود على المناقشة
    c.execute('''
        SELECT dr.id, dr.content, dr.created_at,
               u.id as user_id, u.username, u.avatar_url
        FROM discussion_replies dr
        JOIN users u ON dr.user_id = u.id
        WHERE dr.discussion_id = ?
        ORDER BY dr.created_at
    ''', (discussion_id,))
    
    replies = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return render_template('view_discussion.html', discussion=discussion, replies=replies)

@app.route('/discussions/<int:discussion_id>/reply', methods=['POST'])
def add_reply(discussion_id):
    """إضافة رد على مناقشة"""
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول لإضافة رد', 'warning')
        return redirect(url_for('login', next=url_for('view_discussion', discussion_id=discussion_id)))
    
    content = request.form.get('content')
    
    if not content or not content.strip():
        flash('الرد لا يمكن أن يكون فارغاً', 'danger')
        return redirect(url_for('view_discussion', discussion_id=discussion_id))
    
    conn = sqlite3.connect('analytics.db')
    c = conn.cursor()
    
    # التحقق من وجود المناقشة
    c.execute('SELECT id FROM discussions WHERE id = ?', (discussion_id,))
    if not c.fetchone():
        conn.close()
        flash('المناقشة غير موجودة', 'danger')
        return redirect(url_for('discussions'))
    
    c.execute('''
        INSERT INTO discussion_replies (discussion_id, user_id, content)
        VALUES (?, ?, ?)
    ''', (discussion_id, session['user_id'], content))
    
    conn.commit()
    conn.close()
    
    flash('تمت إضافة الرد بنجاح!', 'success')
    return redirect(url_for('view_discussion', discussion_id=discussion_id))

@app.route('/discussions/<int:discussion_id>/edit', methods=['GET', 'POST'])
def edit_discussion(discussion_id):
    """تعديل مناقشة"""
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول لتعديل المناقشة', 'warning')
        return redirect(url_for('login', next=url_for('view_discussion', discussion_id=discussion_id)))
    
    conn = sqlite3.connect('analytics.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # التحقق من وجود المناقشة وملكيتها
    c.execute('''
        SELECT d.*, u.username, u.avatar_url
        FROM discussions d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = ?
    ''', (discussion_id,))
    
    discussion = c.fetchone()
    if not discussion:
        conn.close()
        flash('المناقشة غير موجودة', 'danger')
        return redirect(url_for('discussions'))
    
    if discussion['user_id'] != session['user_id']:
        conn.close()
        flash('لا يمكنك تعديل هذه المناقشة', 'danger')
        return redirect(url_for('view_discussion', discussion_id=discussion_id))
    
    discussion = dict(discussion)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        tool_id = request.form.get('tool_id') or None
        notifications = 'notifications' in request.form
        
        if not title or not description or not category:
            flash('جميع الحقول المطلوبة يجب ملؤها', 'danger')
        else:
            c.execute('''
                UPDATE discussions
                SET title = ?, description = ?, category = ?, tool_id = ?
                WHERE id = ?
            ''', (title, description, category, tool_id, discussion_id))
            
            conn.commit()
            flash('تم تحديث المناقشة بنجاح!', 'success')
            return redirect(url_for('view_discussion', discussion_id=discussion_id))
    
    # الحصول على قائمة الأدوات للاختيار منها
    c.execute('''
        SELECT id, name FROM tools WHERE status = 'approved'
        ORDER BY name
    ''')
    
    tools = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return render_template('edit_discussion.html', discussion=discussion, tools=tools)

@app.route('/reply/<int:reply_id>/edit', methods=['GET', 'POST'])
def edit_reply(reply_id):
    """تعديل رد"""
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول لتعديل الرد', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('analytics.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # التحقق من وجود الرد وملكيته
    c.execute('''
        SELECT dr.*, d.id as discussion_id, d.title as discussion_title
        FROM discussion_replies dr
        JOIN discussions d ON dr.discussion_id = d.id
        WHERE dr.id = ?
    ''', (reply_id,))
    
    reply = c.fetchone()
    if not reply:
        conn.close()
        flash('الرد غير موجود', 'danger')
        return redirect(url_for('discussions'))
    
    if reply['user_id'] != session['user_id']:
        conn.close()
        flash('لا يمكنك تعديل هذا الرد', 'danger')
        return redirect(url_for('view_discussion', discussion_id=reply['discussion_id']))
    
    reply = dict(reply)
    
    if request.method == 'POST':
        content = request.form.get('content')
        
        if not content or not content.strip():
            flash('الرد لا يمكن أن يكون فارغاً', 'danger')
        else:
            c.execute('''
                UPDATE discussion_replies
                SET content = ?
                WHERE id = ?
            ''', (content, reply_id))
            
            conn.commit()
            flash('تم تحديث الرد بنجاح!', 'success')
            return redirect(url_for('view_discussion', discussion_id=reply['discussion_id']))
    
    # الحصول على معلومات المناقشة
    c.execute('''
        SELECT title
        FROM discussions
        WHERE id = ?
    ''', (reply['discussion_id'],))
    
    discussion = dict(c.fetchone())
    discussion['id'] = reply['discussion_id']
    
    conn.close()
    
    return render_template('edit_reply.html', reply=reply, discussion=discussion)

@app.route('/reply/<int:reply_id>/delete')
def delete_reply(reply_id):
    """حذف رد"""
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول لحذف الرد', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('analytics.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # التحقق من وجود الرد وملكيته
    c.execute('''
        SELECT dr.user_id, dr.discussion_id, u.is_admin
        FROM discussion_replies dr
        JOIN users u ON u.id = ?
        WHERE dr.id = ?
    ''', (session['user_id'], reply_id))
    
    result = c.fetchone()
    if not result:
        conn.close()
        flash('الرد غير موجود', 'danger')
        return redirect(url_for('discussions'))
    
    # التحقق من صلاحية الحذف (مالك الرد أو مشرف)
    if result['user_id'] != session['user_id'] and not result['is_admin']:
        conn.close()
        flash('لا يمكنك حذف هذا الرد', 'danger')
        return redirect(url_for('view_discussion', discussion_id=result['discussion_id']))
    
    discussion_id = result['discussion_id']
    
    c.execute('DELETE FROM discussion_replies WHERE id = ?', (reply_id,))
    conn.commit()
    conn.close()
    
    flash('تم حذف الرد بنجاح', 'success')
    return redirect(url_for('view_discussion', discussion_id=discussion_id))

@app.route('/discussions/<int:discussion_id>/delete')
def delete_discussion(discussion_id):
    """حذف مناقشة"""
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول لحذف المناقشة', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('analytics.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # التحقق من وجود المناقشة وملكيتها
    c.execute('''
        SELECT d.user_id, u.is_admin
        FROM discussions d
        JOIN users u ON u.id = ?
        WHERE d.id = ?
    ''', (session['user_id'], discussion_id))
    
    result = c.fetchone()
    if not result:
        conn.close()
        flash('المناقشة غير موجودة', 'danger')
        return redirect(url_for('discussions'))
    
    # التحقق من صلاحية الحذف (مالك المناقشة أو مشرف)
    if result['user_id'] != session['user_id'] and not result['is_admin']:
        conn.close()
        flash('لا يمكنك حذف هذه المناقشة', 'danger')
        return redirect(url_for('view_discussion', discussion_id=discussion_id))
    
    # حذف جميع الردود المرتبطة بالمناقشة أولاً
    c.execute('DELETE FROM discussion_replies WHERE discussion_id = ?', (discussion_id,))
    
    # ثم حذف المناقشة نفسها
    c.execute('DELETE FROM discussions WHERE id = ?', (discussion_id,))
    
    conn.commit()
    conn.close()
    
    flash('تم حذف المناقشة بنجاح', 'success')
    return redirect(url_for('discussions'))

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
