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
    
    // إضافة بيانات منظمة لتحسين SEO
    addStructuredData();
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

// الأسئلة الشائعة - التوسيع والطي
function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', () => {
            // Toggle active state
            const isActive = item.classList.contains('active');
            
            // Close all items
            faqItems.forEach(faqItem => {
                faqItem.classList.remove('active');
            });
            
            // Open current item (unless it was already open)
            if (!isActive) {
                item.classList.add('active');
            }
        });
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

// إضافة البيانات المنظمة لتحسين SEO
function addStructuredData() {
    const structuredDataSection = document.createElement('script');
    structuredDataSection.type = 'application/ld+json';
    
    const structuredData = {
        "@context": "https://schema.org",
        "@type": "EducationalOrganization",
        "name": "Shifra Community",
        "description": "مجتمع لتعلم الذكاء الاصطناعي باللغة العربية",
        "url": "https://shifra-community.onrender.com/",
        "logo": "https://shifra-community.onrender.com/static/images/shifra-logo.svg",
        "sameAs": [
            "https://www.facebook.com/shifracommunity",
            "https://twitter.com/shifracommunity",
            "https://www.instagram.com/shifracommunity"
        ],
        "offers": {
            "@type": "Offer",
            "price": "1",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": "https://shifra-community.onrender.com/"
        }
    };
    
    structuredDataSection.textContent = JSON.stringify(structuredData);
    document.head.appendChild(structuredDataSection);
    
    // أيضًا نضيف بيانات منظمة للمقالات
    const blogStructuredData = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "item": {
                    "@type": "Article",
                    "name": "مقدمة شاملة في الذكاء الاصطناعي للمبتدئين",
                    "description": "تعرف على المفاهيم الأساسية للذكاء الاصطناعي وكيف يمكنك البدء في تعلم هذا المجال المثير.",
                    "author": {
                        "@type": "Organization",
                        "name": "Shifra Community"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "Shifra Community",
                        "logo": {
                            "@type": "ImageObject",
                            "url": "https://shifra-community.onrender.com/static/images/shifra-logo.svg"
                        }
                    }
                }
            },
            {
                "@type": "ListItem",
                "position": 2,
                "item": {
                    "@type": "Article",
                    "name": "كيفية استخدام ChatGPT لتطوير مشاريعك البرمجية",
                    "description": "دليل عملي لاستخدام ChatGPT في تطوير البرمجيات وتحسين الإنتاجية.",
                    "author": {
                        "@type": "Organization",
                        "name": "Shifra Community"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "Shifra Community",
                        "logo": {
                            "@type": "ImageObject",
                            "url": "https://shifra-community.onrender.com/static/images/shifra-logo.svg"
                        }
                    }
                }
            },
            {
                "@type": "ListItem",
                "position": 3,
                "item": {
                    "@type": "Article",
                    "name": "أساسيات التعلم الآلي: الخوارزميات والتطبيقات",
                    "description": "استكشف عالم التعلم الآلي وأهم الخوارزميات المستخدمة في تحليل البيانات والتنبؤ.",
                    "author": {
                        "@type": "Organization",
                        "name": "Shifra Community"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "Shifra Community",
                        "logo": {
                            "@type": "ImageObject",
                            "url": "https://shifra-community.onrender.com/static/images/shifra-logo.svg"
                        }
                    }
                }
            }
        ]
    };
    
    const blogStructuredDataSection = document.createElement('script');
    blogStructuredDataSection.type = 'application/ld+json';
    blogStructuredDataSection.textContent = JSON.stringify(blogStructuredData);
    document.head.appendChild(blogStructuredDataSection);
    
    // إضافة بيانات منظمة للأسئلة الشائعة
    const faqStructuredData = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "كيف يتم استخدام مبلغ الدولار الواحد؟",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "يتم استخدام مبلغ الدولار الواحد في تطوير المحتوى التعليمي وتحسين المنصة وتنظيم الجلسات المباشرة. هدفنا ليس الربح المادي بل بناء مجتمع تعليمي متكامل يدعم بعضه البعض."
                }
            },
            {
                "@type": "Question",
                "name": "ما هي طرق الدفع المتاحة للاشتراك؟",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "نوفر عدة طرق للدفع تشمل بطاقات الائتمان (Visa/Mastercard)، PayPal، وخيارات دفع محلية في عدة دول عربية. جميع المعاملات مؤمنة بتشفير عالي المستوى."
                }
            },
            {
                "@type": "Question",
                "name": "كيف يمكنني الوصول للمحتوى بعد الانضمام؟",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "بعد الانضمام وتأكيد اشتراكك، ستتلقى بريدًا إلكترونيًا يحتوي على تفاصيل الوصول للمنصة التعليمية. سيكون لديك حساب خاص يتيح لك الوصول لجميع المحتوى التعليمي والمشاركة في الجلسات الأسبوعية."
                }
            }
        ]
    };
    
    const faqStructuredDataSection = document.createElement('script');
    faqStructuredDataSection.type = 'application/ld+json';
    faqStructuredDataSection.textContent = JSON.stringify(faqStructuredData);
    document.head.appendChild(faqStructuredDataSection);
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
