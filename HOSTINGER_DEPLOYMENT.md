# دليل نشر التطبيق على هوستينجر

هذا الدليل يوضح كيفية نشر تطبيق محرر المحتوى بالذكاء الاصطناعي على خدمة الاستضافة هوستينجر.

## متطلبات ما قبل النشر

1. **حساب هوستينجر**: تأكد من وجود حساب نشط مع دعم Python
2. **مفتاح Google Gemini API**: احصل على مفتاح API من Google AI Studio
3. **معرفة أساسية بـ cPanel**: للوصول إلى إدارة الملفات والإعدادات

## خطوات النشر

### الخطوة 1: تحضير الملفات

1. قم بتحميل جميع ملفات المشروع إلى مجلد `public_html` في cPanel
2. تأكد من رفع المجلدات التالية:
   - `templates/` (ملفات HTML)
   - `static/` (ملفات CSS و JavaScript)
   - `app.py` (التطبيق الرئيسي)
   - `requirements.txt` (المتطلبات)

### الخطوة 2: إعداد Python Environment

#### للاستضافة المشتركة (Shared Hosting):

1. افتح Terminal في cPanel
2. أنشئ بيئة Python افتراضية:
```bash
python3.9 -m venv venv
source venv/bin/activate
```

3. قم بتثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

### الخطوة 3: إعداد متغيرات البيئة

1. أنشئ ملف `.env` في المجلد الجذر:
```env
GEMINI_API_KEY=your_actual_api_key_here
FLASK_ENV=production
PORT=5000
```

2. أو قم بإعداد متغيرات البيئة في cPanel:
   - اذهب إلى "Python App" في cPanel
   - أضف المتغيرات في قسم Environment Variables

### الخطوة 4: إعداد Python App في cPanel

1. اذهب إلى "Python App" في cPanel
2. أنشئ تطبيق جديد:
   - **Python Version**: 3.9
   - **Application Root**: `/public_html`
   - **Application URL**: اتركه فارغ للنطاق الرئيسي
   - **Application startup file**: `app.py`
   - **Application Entry point**: `app`

### الخطوة 5: تحديث app.py للإنتاج

تأكد من أن ملف `app.py` يحتوي على هذه التعديلات للإنتاج:

```python
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# قراءة مفتاح API من متغيرات البيئة
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR_DEFAULT_KEY')

# باقي الكود...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
```

### الخطوة 6: إعداد .htaccess (للاستضافة المشتركة)

أنشئ ملف `.htaccess` في `public_html`:

```apache
RewriteEngine On

# إعادة توجيه جميع الطلبات إلى app.py
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /app.py/$1 [QSA,L]

# إعدادات الأمان
<Files "*.py">
    Require all denied
</Files>

<Files "app.py">
    Require all granted
</Files>

# إعدادات Python
AddHandler cgi-script .py
Options +ExecCGI
```

### الخطوة 7: اختبار التطبيق

1. انتظر بضع دقائق حتى يتم تفعيل التطبيق
2. قم بزيارة نطاقك في المتصفح
3. تأكد من عمل جميع الوظائف:
   - تحميل الصفحة الرئيسية
   - فتح المحرر
   - تجربة ميزة تحسين النص

## استكشاف الأخطاء

### مشاكل شائعة وحلولها:

1. **خطأ 500 Internal Server Error**:
   - تحقق من ملف error_log في cPanel
   - تأكد من صحة مسار Python وتثبيت المتطلبات

2. **API لا يعمل**:
   - تأكد من صحة مفتاح Gemini API
   - تحقق من متغيرات البيئة

3. **الملفات الثابتة لا تُحمل**:
   - تأكد من رفع مجلد `static/`
   - تحقق من صحة المسارات في HTML

4. **مشاكل الترميز العربي**:
   - تأكد من أن الملفات محفوظة بترميز UTF-8
   - أضف هذا إلى .htaccess:
   ```apache
   AddDefaultCharset UTF-8
   ```

## إعدادات الأمان

1. **إخفاء مفتاح API**:
   - لا تضع مفتاح API مباشرة في الكود
   - استخدم متغيرات البيئة دائماً

2. **حماية الملفات الحساسة**:
   ```apache
   <Files ".env">
       Require all denied
   </Files>
   ```

3. **تحديد الوصول للمجلدات**:
   ```apache
   <Directory "templates">
       Require all denied
   </Directory>
   ```

## التحديثات والصيانة

1. **تحديث التطبيق**:
   - ارفع الملفات المحدثة عبر File Manager
   - أعد تشغيل Python App من cPanel

2. **مراقبة الأداء**:
   - تابع استخدام الموارد في cPanel
   - راجع سجلات الأخطاء بانتظام

3. **النسخ الاحتياطي**:
   - اعمل نسخة احتياطية من الملفات بانتظام
   - احفظ إعدادات قاعدة البيانات إن وجدت

## دعم إضافي

للحصول على دعم إضافي:
- راجع وثائق هوستينجر للـ Python Apps
- تواصل مع الدعم الفني لهوستينجر
- راجع مجتمع المطورين العرب