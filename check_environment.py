#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
فحص إعدادات البيئة للنشر على هوستينجر
Environment setup checker for Hostinger deployment
"""

import os
import sys

def check_environment():
    """فحص إعدادات البيئة المطلوبة"""
    print("🔍 فحص إعدادات البيئة...")
    print("=" * 50)
    
    checks = []
    
    # فحص Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print(f"✅ إصدار Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
        checks.append(True)
    else:
        print(f"❌ إصدار Python قديم: {python_version.major}.{python_version.minor}.{python_version.micro}")
        print("   يُفضل Python 3.8 أو أحدث")
        checks.append(False)
    
    # فحص الملفات المطلوبة
    required_files = [
        'app.py',
        'requirements.txt',
        'templates/',
        'static/',
        '.htaccess',
        'wsgi.py'
    ]
    
    print("\n📁 فحص الملفات المطلوبة:")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            checks.append(True)
        else:
            print(f"❌ {file_path} - غير موجود")
            checks.append(False)
    
    # فحص متغيرات البيئة
    print("\n🔑 فحص متغيرات البيئة:")
    
    # فحص وجود ملف .env
    if os.path.exists('.env'):
        print("✅ ملف .env موجود")
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'GEMINI_API_KEY' in env_content:
                print("✅ متغير GEMINI_API_KEY موجود في .env")
                checks.append(True)
            else:
                print("❌ متغير GEMINI_API_KEY غير موجود في .env")
                checks.append(False)
    else:
        print("⚠️  ملف .env غير موجود - تأكد من إعداد متغيرات البيئة في cPanel")
        checks.append(None)
    
    # فحص مفتاح API من متغيرات البيئة
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        if api_key != 'your_actual_api_key_here' and len(api_key) > 20:
            print("✅ مفتاح GEMINI_API_KEY مُعرَّف في متغيرات البيئة")
            checks.append(True)
        else:
            print("❌ مفتاح GEMINI_API_KEY غير صحيح أو ما زال القيمة الافتراضية")
            checks.append(False)
    else:
        print("⚠️  مفتاح GEMINI_API_KEY غير مُعرَّف في متغيرات البيئة")
        checks.append(None)
    
    # تجربة استيراد المتطلبات
    print("\n📦 فحص المتطلبات:")
    try:
        import flask
        print(f"✅ Flask مثبت - الإصدار: {flask.__version__}")
        checks.append(True)
    except ImportError:
        print("❌ Flask غير مثبت")
        checks.append(False)
    
    try:
        import flask_cors
        print("✅ Flask-CORS مثبت")
        checks.append(True)
    except ImportError:
        print("❌ Flask-CORS غير مثبت")
        checks.append(False)
    
    try:
        import requests
        print("✅ Requests مثبت")
        checks.append(True)
    except ImportError:
        print("❌ Requests غير مثبت")
        checks.append(False)
    
    # النتيجة النهائية
    print("\n" + "=" * 50)
    successful_checks = sum(1 for check in checks if check is True)
    failed_checks = sum(1 for check in checks if check is False)
    warning_checks = sum(1 for check in checks if check is None)
    total_checks = len([c for c in checks if c is not None])
    
    print(f"📊 نتائج الفحص:")
    print(f"   ✅ نجح: {successful_checks}")
    print(f"   ❌ فشل: {failed_checks}")
    print(f"   ⚠️  تحذير: {warning_checks}")
    
    if failed_checks == 0:
        print("\n🎉 البيئة جاهزة للنشر!")
        print("يمكنك المتابعة مع خطوات النشر على هوستينجر.")
    else:
        print(f"\n⚠️  يجب إصلاح {failed_checks} مشكلة قبل النشر.")
        print("راجع الأخطاء أعلاه وقم بإصلاحها أولاً.")
    
    return failed_checks == 0

if __name__ == '__main__':
    print("مدقق إعدادات البيئة لنشر هوستينجر")
    print("=" * 50)
    success = check_environment()
    sys.exit(0 if success else 1)