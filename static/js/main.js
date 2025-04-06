// سكربت للصفحة الرئيسية
document.addEventListener('DOMContentLoaded', function() {
    console.log('تم تحميل الصفحة بنجاح');
    
    // التحقق مما إذا كان المستخدم على الصفحة الرئيسية
    const isHomePage = window.location.pathname === '/' || window.location.pathname === '/index.html';
    
    if (isHomePage) {
        // تمرير سلس للروابط الداخلية
        const internalLinks = document.querySelectorAll('a[href^="/"]:not([href^="//"])');
        internalLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const href = this.getAttribute('href');
                // تأثير انتقال بسيط
                document.body.style.opacity = 0;
                setTimeout(() => {
                    window.location.href = href;
                }, 300);
            });
        });
        
        // تأثير ظهور لبطاقات المميزات
        const featureCards = document.querySelectorAll('.feature-card');
        if (featureCards.length) {
            featureCards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 100 * index);
            });
        }
    }
});