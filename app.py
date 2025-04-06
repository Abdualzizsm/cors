from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import requests
import json

app = Flask(__name__)
CORS(app)  # لتمكين طلبات CORS للتكامل مع واجهات برمجة الذكاء الاصطناعي

# مفتاح API لـ Google Gemini
GEMINI_API_KEY = "AIzaSyC6ut-z1NNyXy1ErA8nhbrHPeU05qA74Yk"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# صفحة المحرر
@app.route('/editor')
def editor():
    return render_template('editor.html')

# واجهة برمجة لتلقي المحتوى المكتوب وإرساله للذكاء الاصطناعي
@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    data = request.json
    user_text = data.get('text', '')
    content_type = data.get('type', 'article')
    
    if not user_text:
        return jsonify({
            'original': user_text,
            'enhanced': 'لا يوجد نص للتحسين',
            'suggestions': ['أدخل نصًا للحصول على اقتراحات']
        })
    
    # تحضير الموجه حسب نوع المحتوى
    prompt_prefix = "أنت كاتب محترف. "
    
    if content_type == 'article':
        prompt = f"{prompt_prefix}قم بتحسين هذا المقال مع الحفاظ على أسلوبه وأفكاره الرئيسية: {user_text}"
    elif content_type == 'product':
        prompt = f"{prompt_prefix}قم بتحسين وصف المنتج التالي ليكون أكثر جاذبية وإقناعًا للمشترين: {user_text}"
    elif content_type == 'social':
        prompt = f"{prompt_prefix}قم بتحسين هذا المنشور لوسائل التواصل الاجتماعي ليكون أكثر تفاعلًا: {user_text}"
    elif content_type == 'email':
        prompt = f"{prompt_prefix}قم بتحسين هذا البريد الإلكتروني التسويقي ليكون أكثر إقناعًا: {user_text}"
    else:
        prompt = f"{prompt_prefix}قم بتحسين النص التالي: {user_text}"
    
    # إضافة طلب للاقتراحات
    suggestions_prompt = f"قدم 3 اقتراحات لتحسين النص التالي بشكل أكبر: {user_text}"
    
    try:
        # طلب تحسين النص
        enhanced_text = call_gemini_api(prompt)
        
        # طلب اقتراحات
        suggestions_text = call_gemini_api(suggestions_prompt)
        
        # معالجة الاقتراحات - تقسيمها إلى قائمة
        suggestions = process_suggestions(suggestions_text)
        
        ai_response = {
            'original': user_text,
            'enhanced': enhanced_text,
            'suggestions': suggestions
        }
        
        return jsonify(ai_response)
    
    except Exception as e:
        print(f"خطأ في استدعاء Gemini API: {str(e)}")
        # استخدام المحاكاة كاحتياطي في حالة فشل API
        ai_response = {
            'original': user_text,
            'enhanced': f"تم تحسين: {user_text}\n(ملاحظة: تم استخدام المحاكاة لأن API الفعلي واجه مشكلة)",
            'suggestions': [
                "يمكنك تحسين المقدمة",
                "أضف المزيد من الكلمات المفتاحية",
                "قم بتقسيم الفقرات لتسهيل القراءة"
            ]
        }
        return jsonify(ai_response)

# استدعاء واجهة برمجة Gemini
def call_gemini_api(prompt):
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        response_data = response.json()
        # استخراج النص من استجابة API
        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            if "content" in response_data["candidates"][0]:
                content = response_data["candidates"][0]["content"]
                if "parts" in content and len(content["parts"]) > 0:
                    return content["parts"][0]["text"]
    
    # إذا لم يتم العثور على النص في الاستجابة
    raise Exception(f"فشل في استخراج النص من الاستجابة: {response.text}")

# معالجة نص الاقتراحات وتحويله إلى قائمة
def process_suggestions(suggestions_text):
    # تقسيم النص إلى أسطر
    lines = suggestions_text.split('\n')
    # تنظيف وتصفية الأسطر
    suggestions = []
    for line in lines:
        line = line.strip()
        # إزالة الأرقام والنقاط في بداية السطر
        line = line.lstrip('0123456789.- ')
        if line and len(line) > 5:  # فقط الأسطر ذات المحتوى المعقول
            suggestions.append(line)
    
    # التأكد من أن لدينا على الأقل بعض الاقتراحات
    if len(suggestions) < 1:
        # تقسيم النص إلى جمل بدلاً من ذلك
        sentences = suggestions_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:
                suggestions.append(sentence)
    
    # الحد إلى 3 اقتراحات كحد أقصى
    return suggestions[:3] if len(suggestions) > 3 else suggestions

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)