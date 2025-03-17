from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import logging
from datetime import datetime

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
    return send_from_directory('static', 'sitemap.xml')

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
