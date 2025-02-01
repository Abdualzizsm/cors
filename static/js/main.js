// Counter Animation
document.addEventListener('DOMContentLoaded', function() {
    // Seats counter animation
    const seatsCounter = document.getElementById('seatsCounter');
    if (seatsCounter) {
        const targetSeats = 5; // Set your desired number
        let currentSeats = targetSeats;
        
        // Update counter every 3 hours (simulating seats being taken)
        setInterval(() => {
            if (currentSeats > 1) {
                currentSeats--;
                seatsCounter.textContent = currentSeats;
                
                // Add urgency when seats are low
                if (currentSeats <= 3) {
                    seatsCounter.classList.add('text-danger');
                }
            }
        }, 3 * 60 * 60 * 1000); // 3 hours in milliseconds
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add animation to elements when they come into view
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.card, .section-title, .feature-item');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
            element.classList.add('fade-in');
        }
    });
}

window.addEventListener('scroll', animateOnScroll);

// Countdown Timer
function startCountdown() {
    const countdownElement = document.getElementById('countdown');
    if (!countdownElement) return;

    let hours = 23;
    let minutes = 59;
    let seconds = 59;

    setInterval(() => {
        if (seconds > 0) {
            seconds--;
        } else {
            seconds = 59;
            if (minutes > 0) {
                minutes--;
            } else {
                minutes = 59;
                if (hours > 0) {
                    hours--;
                }
            }
        }

        countdownElement.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
}

// Real-time Viewers Update
function updateViewers() {
    const minViewers = 12;
    const maxViewers = 25;
    
    setInterval(() => {
        const viewers = Math.floor(Math.random() * (maxViewers - minViewers + 1)) + minViewers;
        const viewersElement = document.querySelector('.last-registration p:last-child');
        if (viewersElement) {
            viewersElement.innerHTML = `<i class="fas fa-eye me-2"></i>${viewers} شخص يشاهدون هذه الصفحة الآن`;
        }
    }, 5000);
}

// Last Registration Update
function updateLastRegistration() {
    const lastRegElement = document.querySelector('.last-registration p:first-child');
    if (!lastRegElement) return;

    const times = ['قبل دقيقة', 'قبل 2 دقائق', 'قبل 3 دقائق', 'قبل 4 دقائق'];
    let index = 0;

    setInterval(() => {
        lastRegElement.innerHTML = `<i class="fas fa-user-check me-2"></i>آخر تسجيل: ${times[index]}`;
        index = (index + 1) % times.length;
    }, 15000);
}

// Available Seats Update
function updateAvailableSeats() {
    const seatsElement = document.querySelector('.urgency .text-danger');
    if (!seatsElement) return;

    const initialSeats = 5;
    let availableSeats = initialSeats;

    setInterval(() => {
        if (Math.random() < 0.3 && availableSeats > 1) {
            availableSeats--;
            const progressBar = document.querySelector('.progress-bar');
            const percentage = ((initialSeats - availableSeats) / initialSeats) * 100;
            
            if (progressBar) {
                progressBar.style.width = `${85 + percentage}%`;
                progressBar.innerHTML = `<span>${85 + percentage}% من المقاعد محجوزة</span>`;
            }
            
            seatsElement.textContent = `متبقي ${availableSeats} مقاعد فقط!`;
        }
    }, 30000);
}

// Contact Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value.trim();
            const phone = document.getElementById('phone').value.trim();
            
            // التحقق من صحة رقم الهاتف
            if (!phone.match(/^05[0-9]{8}$/)) {
                alert('الرجاء إدخال رقم جوال صحيح يبدأ بـ 05');
                return;
            }
            
            // تنسيق رقم الهاتف للواتساب
            const formattedPhone = '966' + phone.substring(1);
            
            // إنشاء رسالة الواتساب
            const message = `مرحباً، أنا ${name} وأرغب في الاستفسار عن كورس البرمجة`;
            const whatsappUrl = `https://wa.me/${formattedPhone}?text=${encodeURIComponent(message)}`;
            
            // فتح الواتساب
            window.open(whatsappUrl, '_blank');
        });
    }
});

// Initialize all functions
document.addEventListener('DOMContentLoaded', () => {
    startCountdown();
    updateViewers();
    updateLastRegistration();
    updateAvailableSeats();
});
