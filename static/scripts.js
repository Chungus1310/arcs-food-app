document.addEventListener('DOMContentLoaded', function() {
    // Animate stat numbers
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        const number = card.querySelector('.stat-number');
        const targetValue = parseInt(card.dataset.value);
        animateNumber(number, targetValue);
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
});

// Enhanced animations and interaction handling
function animateNumber(element, target) {
    const duration = 1500;
    const steps = 60;
    const stepDuration = duration / steps;
    let current = 0;
    
    const easeOutQuart = x => 1 - Math.pow(1 - x, 4);
    
    const animate = (currentStep) => {
        if (currentStep === steps) {
            element.textContent = target.toLocaleString();
            return;
        }
        
        const progress = easeOutQuart(currentStep / steps);
        current = Math.round(target * progress);
        element.textContent = current.toLocaleString();
        
        setTimeout(() => animate(currentStep + 1), stepDuration);
    };
    
    animate(0);
}

// Smooth scroll with dynamic offset based on navbar height
function smoothScroll(target) {
    const navbar = document.querySelector('.navbar');
    const navbarHeight = navbar.getBoundingClientRect().height;
    const targetElement = document.querySelector(target);
    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
    
    window.scrollTo({
        top: targetPosition - navbarHeight - 20,
        behavior: 'smooth'
    });
}

// Enhanced touch interaction handling
function initializeTouchInteractions() {
    const interactiveElements = document.querySelectorAll('.stat-card, .action-card, .btn');
    
    interactiveElements.forEach(element => {
        element.addEventListener('touchstart', () => {
            element.style.transform = 'scale(0.98)';
        }, { passive: true });
        
        element.addEventListener('touchend', () => {
            element.style.transform = '';
        }, { passive: true });
    });
}

// Add hover effects for cards
document.querySelectorAll('.stat-card, .action-card').forEach(card => {
    card.addEventListener('mouseover', function() {
        this.style.transform = 'translateY(-5px)';
    });
    
    card.addEventListener('mouseout', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Enhanced Animations and Interactions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add intersection observer for animation on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    // Observe all cards
    document.querySelectorAll('.stat-card, .action-card').forEach(card => {
        observer.observe(card);
    });
});