// سكربت خاص بصفحة المحرر
document.addEventListener('DOMContentLoaded', function() {
    // التحقق من وجود المحرر في الصفحة
    if (document.getElementById('editor')) {
        // تهيئة محرر TinyMCE
        tinymce.init({
            selector: '#editor',
            directionality: 'rtl', // الاتجاه من اليمين إلى اليسار للغة العربية
            height: 500,
            menubar: false,
            plugins: [
                'advlist autolink lists link image charmap print preview anchor',
                'searchreplace visualblocks code fullscreen',
                'insertdatetime media table paste code help wordcount'
            ],
            toolbar: 'undo redo | formatselect | bold italic backcolor | \
                alignright aligncenter alignleft alignjustify | \
                bullist numlist outdent indent | removeformat | help',
            content_style: 'body { font-family:Tahoma,Arial,sans-serif; font-size:16px }',
            language: 'ar', // تعيين لغة المحرر إلى العربية
            setup: function(editor) {
                // إضافة خاصية الحفظ التلقائي
                setInterval(function() {
                    if (editor.isDirty()) {
                        localStorage.setItem('autosave', editor.getContent());
                        console.log('تم الحفظ التلقائي');
                    }
                }, 60000); // حفظ كل دقيقة
            }
        });

        // تنفيذ وظيفة معاينة المحتوى
        document.getElementById('preview-btn').addEventListener('click', function() {
            const content = tinymce.get('editor').getContent();
            document.getElementById('preview-content').innerHTML = content;
            document.querySelector('.editor-area').classList.add('hidden');
            document.getElementById('preview-area').classList.remove('hidden');
        });

        // العودة من المعاينة إلى التحرير
        document.getElementById('close-preview').addEventListener('click', function() {
            document.getElementById('preview-area').classList.add('hidden');
            document.querySelector('.editor-area').classList.remove('hidden');
        });

        // حفظ المحتوى
        document.getElementById('save-btn').addEventListener('click', function() {
            const content = tinymce.get('editor').getContent();
            const title = document.getElementById('content-title').value;
            
            // محاكاة الحفظ - في التطبيق الفعلي سيتم إرسال البيانات إلى الخادم
            localStorage.setItem('savedContent', content);
            localStorage.setItem('savedTitle', title);
            
            alert('تم حفظ المحتوى بنجاح!');
        });
        
        // التفاعل مع الذكاء الاصطناعي لتحسين المحتوى
        document.getElementById('generate-btn').addEventListener('click', function() {
            const content = tinymce.get('editor').getContent();
            const contentType = document.getElementById('content-type').value;
            
            // عرض حالة التحميل
            this.textContent = 'جاري التحسين...';
            this.disabled = true;
            
            // إرسال المحتوى إلى واجهة برمجة التطبيق
            fetch('/api/generate-content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: extractTextFromHTML(content),
                    type: contentType
                }),
            })
            .then(response => response.json())
            .then(data => {
                // تحديث المحتوى بالنص المحسن
                tinymce.get('editor').setContent(data.enhanced);
                
                // عرض الاقتراحات
                displaySuggestions(data.suggestions);
                
                // إعادة الزر إلى حالته الأصلية
                document.getElementById('generate-btn').textContent = 'تحسين المحتوى';
                document.getElementById('generate-btn').disabled = false;
            })
            .catch(error => {
                console.error('حدث خطأ:', error);
                alert('حدث خطأ أثناء تحسين المحتوى. يرجى المحاولة مرة أخرى.');
                document.getElementById('generate-btn').textContent = 'تحسين المحتوى';
                document.getElementById('generate-btn').disabled = false;
            });
        });
        
        // استخراج النص من المحتوى HTML
        function extractTextFromHTML(html) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            return tempDiv.textContent || tempDiv.innerText || '';
        }
        
        // عرض الاقتراحات
        function displaySuggestions(suggestions) {
            const suggestionsList = document.getElementById('suggestions-list');
            suggestionsList.innerHTML = '';
            
            suggestions.forEach(suggestion => {
                const li = document.createElement('li');
                li.textContent = suggestion;
                li.addEventListener('click', function() {
                    const content = tinymce.get('editor').getContent();
                    // إضافة الاقتراح كتعليق في نهاية المحتوى
                    tinymce.get('editor').setContent(content + '<p><em>ملاحظة: ' + suggestion + '</em></p>');
                });
                suggestionsList.appendChild(li);
            });
        }
        
        // زر اقتراح الأفكار
        document.getElementById('suggest-btn').addEventListener('click', function() {
            const contentType = document.getElementById('content-type').value;
            let suggestions = [];
            
            // محاكاة لاقتراحات حسب نوع المحتوى
            switch(contentType) {
                case 'article':
                    suggestions = [
                        "أضف مقدمة تجذب القراء",
                        "اختم المقال بدعوة للتفاعل",
                        "أضف عناوين فرعية لتقسيم المقال"
                    ];
                    break;
                case 'product':
                    suggestions = [
                        "ركز على فوائد المنتج وليس مميزاته فقط",
                        "أضف مراجعات إيجابية للمنتج",
                        "اذكر عروضًا خاصة أو خصومات"
                    ];
                    break;
                case 'social':
                    suggestions = [
                        "استخدم هاشتاجات ذات صلة",
                        "اجعل المنشور قصيرًا ومباشرًا",
                        "أضف دعوة للتفاعل"
                    ];
                    break;
                case 'email':
                    suggestions = [
                        "استخدم عنوانًا جذابًا للبريد",
                        "ابدأ برسالة شخصية",
                        "اجعل الرسالة مختصرة وواضحة"
                    ];
                    break;
            }
            
            displaySuggestions(suggestions);
        });
        
        // استعادة المحتوى المحفوظ تلقائيًا
        const autosaved = localStorage.getItem('autosave');
        if (autosaved) {
            const restoreConfirm = confirm('هناك محتوى محفوظ تلقائيًا. هل ترغب في استعادته؟');
            if (restoreConfirm) {
                tinymce.get('editor').setContent(autosaved);
            }
        }
    }
});