#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نص بدء التشغيل للاستضافة على هوستينجر
Startup script for Hostinger hosting
"""

import sys
import os

# إضافة مسار المشروع إلى Python path
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# تحميل متغيرات البيئة من ملف .env إذا كان موجوداً
env_path = os.path.join(project_path, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# استيراد وتشغيل التطبيق
try:
    from app import app
    
    if __name__ == '__main__':
        # إعدادات الإنتاج
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
        
        app.run(host=host, port=port, debug=debug)
        
except Exception as e:
    print(f"Error starting application: {str(e)}", file=sys.stderr)
    sys.exit(1)