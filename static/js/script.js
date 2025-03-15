/**
 * شفرة - موقع تعليم الذكاء الاصطناعي
 * ملف JavaScript للوظائف التفاعلية
 */

// تهيئة التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    // تهيئة العداد التنازلي
    initCountdown();
    
    // تهيئة قائمة الجوال
    initMobileMenu();
    
    // تهيئة التمرير السلس
    initSmoothScroll();
    
    // تهيئة تأثيرات التمرير
    initScrollEffects();
});

/**
 * تهيئة العداد التنازلي
 */
function initCountdown() {
    // تاريخ انتهاء العرض (بعد 3 أيام من الآن)
    const now = new Date();
    const endDate = new Date(now);
    endDate.setDate(now.getDate() + 3);
    endDate.setHours(23, 59, 59, 0);
    
    // عناصر العداد التنازلي
    const daysElement = document.getElementById('days');
    const hoursElement = document.getElementById('hours');
    const minutesElement = document.getElementById('minutes');
    const secondsElement = document.getElementById('seconds');
    
    // تحديث العداد التنازلي كل ثانية
    updateCountdown();
    setInterval(updateCountdown, 1000);
    
    function updateCountdown() {
        const currentTime = new Date();
        const timeDifference = endDate - currentTime;
        
        // التحقق مما إذا انتهى العداد التنازلي
        if (timeDifference <= 0) {
            daysElement.textContent = '00';
            hoursElement.textContent = '00';
            minutesElement.textContent = '00';
            secondsElement.textContent = '00';
            return;
        }
        
        // حساب الأيام والساعات والدقائق والثواني المتبقية
        const days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeDifference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);
        
        // تحديث عناصر العداد التنازلي
        daysElement.textContent = days < 10 ? `0${days}` : days;
        hoursElement.textContent = hours < 10 ? `0${hours}` : hours;
        minutesElement.textContent = minutes < 10 ? `0${minutes}` : minutes;
        secondsElement.textContent = seconds < 10 ? `0${seconds}` : seconds;
    }
}

/**
 * تهيئة قائمة الجوال
 */
function initMobileMenu() {
    const menuToggle = document.getElementById('mobile-menu-toggle');
    const mainMenu = document.getElementById('main-menu');
    
    if (menuToggle && mainMenu) {
        menuToggle.addEventListener('click', () => {
            menuToggle.classList.toggle('active');
            mainMenu.classList.toggle('active');
            
            // تغيير خاصية aria-expanded
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !isExpanded);
        });
        
        // إغلاق القائمة عند النقر على أي رابط فيها
        const menuLinks = mainMenu.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                menuToggle.classList.remove('active');
                mainMenu.classList.remove('active');
                menuToggle.setAttribute('aria-expanded', 'false');
            });
        });
    }
}

/**
 * تهيئة التمرير السلس
 */
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const offsetTop = targetElement.getBoundingClientRect().top + window.pageYOffset;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * تهيئة تأثيرات التمرير
 */
function initScrollEffects() {
    // إضافة فئة active عند التمرير
    const elementsToAnimate = document.querySelectorAll('.feature-card, .pricing-card, .stat-card');
    
    // دالة للتحقق مما إذا كان العنصر مرئيًا
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8
        );
    }
    
    // دالة لتحديث حالة العناصر عند التمرير
    function checkElements() {
        elementsToAnimate.forEach(element => {
            if (isElementInViewport(element)) {
                element.classList.add('visible');
            }
        });
    }
    
    // التحقق عند تحميل الصفحة
    checkElements();
    
    // التحقق عند التمرير
    window.addEventListener('scroll', checkElements);
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
