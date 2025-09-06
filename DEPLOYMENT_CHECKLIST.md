# قائمة مراجعة النشر على هوستينجر
# Hostinger Deployment Checklist

## ✅ ما قبل النشر (Pre-deployment)
- [ ] التأكد من وجود حساب هوستينجر نشط مع دعم Python
- [ ] الحصول على مفتاح Google Gemini API
- [ ] تجميع جميع ملفات المشروع

## ✅ رفع الملفات (File Upload)
- [ ] رفع `app.py` إلى public_html
- [ ] رفع مجلد `templates/` كاملاً
- [ ] رفع مجلد `static/` كاملاً
- [ ] رفع `requirements.txt`
- [ ] رفع `.htaccess` (إعدادات الخادم)
- [ ] رفع `wsgi.py` (نص بدء التشغيل)

## ✅ إعداد Python في cPanel
- [ ] الذهاب إلى "Python App" في cPanel
- [ ] إنشاء تطبيق جديد:
  - [ ] Python Version: 3.9 أو أحدث
  - [ ] Application Root: /public_html
  - [ ] Application startup file: app.py
  - [ ] Application Entry point: app

## ✅ إعداد البيئة والمتغيرات
- [ ] إنشاء ملف `.env` في المجلد الجذر
- [ ] إضافة `GEMINI_API_KEY=your_actual_key` في .env
- [ ] إضافة `FLASK_ENV=production` في .env
- [ ] أو إضافة المتغيرات في cPanel > Python App > Environment Variables

## ✅ تثبيت المتطلبات
- [ ] فتح Terminal في cPanel
- [ ] تشغيل: `source /home/username/virtualenv/public_html/3.9/bin/activate`
- [ ] تشغيل: `pip install -r requirements.txt`

## ✅ الاختبار والتأكد
- [ ] انتظار 2-3 دقائق لتفعيل التطبيق
- [ ] زيارة النطاق في المتصفح
- [ ] اختبار تحميل الصفحة الرئيسية
- [ ] اختبار صفحة المحرر
- [ ] اختبار ميزة تحسين النص بالذكاء الاصطناعي

## 🔧 في حالة وجود مشاكل
- [ ] مراجعة سجل الأخطاء في cPanel
- [ ] التأكد من صحة مفتاح API
- [ ] التأكد من تثبيت جميع المتطلبات
- [ ] التأكد من صحة ملف .htaccess
- [ ] مراجعة ملف [دليل النشر المفصل](HOSTINGER_DEPLOYMENT.md)

## 📱 معلومات مهمة للتواصل مع الدعم
- نوع التطبيق: Flask Python Web App
- إصدار Python: 3.9+
- الملفات الرئيسية: app.py, requirements.txt, .htaccess
- نوع الاستضافة: مطلوبة استضافة مع دعم Python

---
💡 **نصيحة**: احتفظ بنسخة احتياطية من جميع الملفات قبل النشر!