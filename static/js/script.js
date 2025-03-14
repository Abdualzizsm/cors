import { gsap } from 'gsap';
import { ScrollTrigger } from "https://cdn.jsdelivr.net/npm/gsap@3.12.2/ScrollTrigger.min.js";

document.addEventListener('DOMContentLoaded', function() {
    // Register ScrollTrigger plugin
    gsap.registerPlugin(ScrollTrigger);
    
    // Initialize mobile menu
    initMobileMenu();
    
    // Initialize animations
    initAnimations();
    
    // Initialize testimonial slider
    initTestimonialSlider();
    
    // Initialize FAQ accordion
    initFaqAccordion();
    
    // Initialize payment method selection
    initPaymentMethodSelector();
    
    // Initialize form submission
    initFormSubmission();
});

function initMobileMenu() {
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.querySelector('nav ul');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            menuToggle.querySelector('i').classList.toggle('fa-bars');
            menuToggle.querySelector('i').classList.toggle('fa-times');
        });
    }
    
    // Close menu when clicking on a link
    const navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            if (menuToggle.querySelector('i').classList.contains('fa-times')) {
                menuToggle.querySelector('i').classList.remove('fa-times');
                menuToggle.querySelector('i').classList.add('fa-bars');
            }
        });
    });
}

function initAnimations() {
    // Hero section animations
    gsap.from('.hero-content', {
        opacity: 0,
        y: 50,
        duration: 1,
        ease: 'power3.out'
    });
    
    gsap.from('.hero-image', {
        opacity: 0,
        y: 30,
        delay: 0.3,
        duration: 1,
        ease: 'power3.out'
    });
    
    // Code typing animation
    const codeLines = document.querySelectorAll('.code-line');
    gsap.from(codeLines, {
        opacity: 0,
        y: 10,
        duration: 0.5,
        stagger: 0.1,
        delay: 1,
        ease: 'power2.out'
    });
    
    // Stats section
    gsap.from('.stat-card', {
        scrollTrigger: {
            trigger: '.stats-section',
            start: 'top 80%'
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        stagger: 0.1,
        ease: 'power2.out'
    });
    
    // Why section
    gsap.from('.feature-point', {
        scrollTrigger: {
            trigger: '.why-section',
            start: 'top 80%'
        },
        opacity: 0,
        x: -30,
        duration: 0.8,
        stagger: 0.2,
        ease: 'power2.out'
    });
    
    gsap.from('.comparison-card', {
        scrollTrigger: {
            trigger: '.comparison-card',
            start: 'top 80%'
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power2.out'
    });
    
    // Features section
    gsap.from('.feature-card', {
        scrollTrigger: {
            trigger: '.features-section',
            start: 'top 80%'
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        stagger: 0.1,
        ease: 'power2.out'
    });
    
    // Program timeline
    gsap.from('.timeline-item', {
        scrollTrigger: {
            trigger: '.program-section',
            start: 'top 80%'
        },
        opacity: 0,
        x: 30,
        duration: 0.8,
        stagger: 0.2,
        ease: 'power2.out'
    });
    
    // Tools section
    gsap.from('.tool-card', {
        scrollTrigger: {
            trigger: '.tools-section',
            start: 'top 80%'
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        stagger: 0.1,
        ease: 'power2.out'
    });
    
    // Instructor section
    gsap.from('.instructor-card', {
        scrollTrigger: {
            trigger: '.instructor-section',
            start: 'top 80%'
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power2.out'
    });
    
    // Register section
    gsap.from('.register-card', {
        scrollTrigger: {
            trigger: '.register-section',
            start: 'top 80%'
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power2.out'
    });
}

function initTestimonialSlider() {
    const slider = document.querySelector('.testimonials-slider');
    if (!slider) return;
    
    const cards = document.querySelectorAll('.testimonial-card');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    let currentIndex = 0;
    
    function showCard(index) {
        // Hide all cards
        cards.forEach(card => {
            card.style.display = 'none';
        });
        
        // Show the current card
        cards[index].style.display = 'block';
        
        // Animate the current card
        gsap.fromTo(cards[index], 
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }
        );
    }
    
    // Initial display
    showCard(currentIndex);
    
    // Event listeners for buttons
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + cards.length) % cards.length;
            showCard(currentIndex);
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % cards.length;
            showCard(currentIndex);
        });
    }
    
    // Auto rotation
    setInterval(() => {
        currentIndex = (currentIndex + 1) % cards.length;
        showCard(currentIndex);
    }, 5000);
}

function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            
            // Close all items
            faqItems.forEach(faq => {
                faq.classList.remove('active');
            });
            
            // Open clicked item if it wasn't active
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });
}

function initPaymentMethodSelector() {
    const paymentMethodSelect = document.getElementById('paymentMethod');
    const creditCardDetails = document.querySelector('.credit-card-details');
    
    if (paymentMethodSelect && creditCardDetails) {
        paymentMethodSelect.addEventListener('change', () => {
            if (paymentMethodSelect.value === 'credit' || paymentMethodSelect.value === 'mada') {
                creditCardDetails.style.display = 'block';
            } else {
                creditCardDetails.style.display = 'none';
            }
        });
    }
}

function initFormSubmission() {
    const paymentForm = document.getElementById('paymentForm');
    
    if (paymentForm) {
        paymentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Simple validation
            const fullName = document.getElementById('fullName').value;
            const email = document.getElementById('email').value;
            const phone = document.getElementById('phone').value;
            const paymentMethod = document.getElementById('paymentMethod').value;
            
            if (!fullName || !email || !phone || !paymentMethod) {
                alert('الرجاء إكمال جميع الحقول المطلوبة');
                return;
            }
            
            // In a real application, you would submit the form data to a server
            // For this example, just show a success message
            alert('تم إكمال عملية الشراء بنجاح! سيتم إرسال تفاصيل الوصول إلى بريدك الإلكتروني.');
            
            // Reset form
            paymentForm.reset();
        });
    }
}