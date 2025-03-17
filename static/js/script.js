/**
 * شفرة - موقع تعليم الذكاء الاصطناعي
 * ملف JavaScript للوظائف التفاعلية
 */

document.addEventListener('DOMContentLoaded', function() {
    // تهيئة العد التنازلي
    initCountdown();
    
    // تفعيل القائمة المتنقلة في الهواتف المحمولة
    initMobileMenu();
    
    // تمرير سلس للروابط الداخلية
    initSmoothScrolling();
    
    // تفعيل الأسئلة الشائعة
    initFaqAccordion();
    
    // تحريك رأس الصفحة عند التمرير
    initHeaderScroll();
});

// تهيئة العد التنازلي
function initCountdown() {
    // تاريخ انتهاء العرض (4 أيام من الآن)
    const now = new Date();
    const targetDate = new Date(now);
    targetDate.setDate(now.getDate() + 4);
    
    // عناصر العد التنازلي
    const daysElement = document.getElementById('timer-days');
    const hoursElement = document.getElementById('timer-hours');
    const minutesElement = document.getElementById('timer-minutes');
    const secondsElement = document.getElementById('timer-seconds');
    
    if (!daysElement || !hoursElement || !minutesElement || !secondsElement) {
        // محاولة الوصول إلى عناصر العد التنازلي القديمة
        const daysOld = document.getElementById('countdown-days');
        const hoursOld = document.getElementById('countdown-hours');
        const minutesOld = document.getElementById('countdown-minutes');
        const secondsOld = document.getElementById('countdown-seconds');
        
        if (daysOld && hoursOld && minutesOld && secondsOld) {
            function updateOldCountdown() {
                const now = new Date();
                const difference = targetDate - now;
                
                if (difference < 0) {
                    // إعادة تعيين العد التنازلي إذا انتهى
                    targetDate.setDate(now.getDate() + 4);
                    updateOldCountdown();
                    return;
                }
                
                // حساب الوقت المتبقي
                const days = Math.floor(difference / (1000 * 60 * 60 * 24));
                const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((difference % (1000 * 60)) / 1000);
                
                // تحديث العناصر
                daysOld.textContent = String(days).padStart(2, '0');
                hoursOld.textContent = String(hours).padStart(2, '0');
                minutesOld.textContent = String(minutes).padStart(2, '0');
                secondsOld.textContent = String(seconds).padStart(2, '0');
            }
            
            // تحديث العد التنازلي كل ثانية
            updateOldCountdown();
            setInterval(updateOldCountdown, 1000);
        }
        return;
    }
    
    function updateCountdown() {
        const now = new Date();
        const difference = targetDate - now;
        
        if (difference < 0) {
            // إعادة تعيين العد التنازلي إذا انتهى
            targetDate.setDate(now.getDate() + 4);
            updateCountdown();
            return;
        }
        
        // حساب الوقت المتبقي
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);
        
        // تحديث العناصر
        daysElement.textContent = String(days).padStart(2, '0');
        hoursElement.textContent = String(hours).padStart(2, '0');
        minutesElement.textContent = String(minutes).padStart(2, '0');
        secondsElement.textContent = String(seconds).padStart(2, '0');
    }
    
    // تحديث العد التنازلي كل ثانية
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

// تفعيل القائمة المتحركة في الهواتف
function initMobileMenu() {
    const menuToggle = document.getElementById('menu-toggle');
    const mainMenu = document.getElementById('main-menu');
    
    if (!menuToggle || !mainMenu) {
        console.warn('لم يتم العثور على عناصر القائمة المتنقلة');
        return;
    }
    
    menuToggle.addEventListener('click', function() {
        menuToggle.classList.toggle('active');
        mainMenu.classList.toggle('active');
    });
    
    // إغلاق القائمة عند النقر على أي رابط
    const menuLinks = mainMenu.querySelectorAll('a');
    menuLinks.forEach(link => {
        link.addEventListener('click', function() {
            menuToggle.classList.remove('active');
            mainMenu.classList.remove('active');
        });
    });
}

// تمرير سلس للروابط الداخلية
function initSmoothScrolling() {
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (!targetElement) return;
            
            const headerOffset = 80;
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        });
    });
}

// تفعيل الأسئلة الشائعة (الأكورديون)
function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const questionElement = item.querySelector('.faq-question');
        
        if (questionElement) {
            questionElement.addEventListener('click', function() {
                // إغلاق جميع الأسئلة المفتوحة
                faqItems.forEach(otherItem => {
                    if (otherItem !== item) {
                        otherItem.classList.remove('active');
                    }
                });
                
                // تبديل حالة السؤال المحدد
                item.classList.toggle('active');
            });
        }
    });
}

// تغيير حجم رأس الصفحة عند التمرير
function initHeaderScroll() {
    const header = document.querySelector('.site-header');
    if (!header) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('shrink');
        } else {
            header.classList.remove('shrink');
        }
    });
}

/**
 * إضافة فئة CSS للعناصر الظاهرة
 */
document.addEventListener('DOMContentLoaded', () => {
    const style = document.createElement('style');
    style.textContent = `
        .feature-card, .pricing-card, .stat-card {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .feature-card.visible, .pricing-card.visible, .stat-card.visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        .feature-card:nth-child(2), .pricing-card:nth-child(2), .stat-card:nth-child(2) {
            transition-delay: 0.2s;
        }
        
        .feature-card:nth-child(3), .pricing-card:nth-child(3), .stat-card:nth-child(3) {
            transition-delay: 0.4s;
        }
        
        .feature-card:nth-child(4), .stat-card:nth-child(4) {
            transition-delay: 0.6s;
        }
        
        .feature-card:nth-child(5) {
            transition-delay: 0.8s;
        }
        
        .feature-card:nth-child(6) {
            transition-delay: 1s;
        }
    `;
    document.head.appendChild(style);
});
