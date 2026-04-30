document.addEventListener('DOMContentLoaded', () => {
    // Intersection Observer for scroll animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all elements with .animate class
    document.querySelectorAll('.animate').forEach(el => {
        observer.observe(el);
    });

    // Also observe cards that don't have animate class yet
    document.querySelectorAll('.card, .model-card, .dept-section, .feature-item, .rec-card, .task-card, .case-item').forEach((el, index) => {
        if (!el.classList.contains('animate')) {
            el.classList.add('animate');
            el.style.transitionDelay = `${index * 0.05}s`;
            observer.observe(el);
        }
    });

    // Mobile nav toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Navbar background on scroll
    const nav = document.getElementById('nav');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            nav.style.background = 'rgba(10,10,15,0.95)';
        } else {
            nav.style.background = 'rgba(10,10,15,0.8)';
        }
        
        lastScroll = currentScroll;
    });
});
