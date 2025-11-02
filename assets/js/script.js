/**
 * Arztpraxis - Medical Practice Website
 * JavaScript for interactivity and form handling
 */

(function() {
    'use strict';

    // ==========================================
    // Mobile Navigation Toggle
    // ==========================================
    const mobileToggle = document.getElementById('mobileToggle');
    const navMenu = document.getElementById('navMenu');

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            navMenu.classList.toggle('active');
            mobileToggle.classList.toggle('active');

            // Prevent body scroll when menu is open
            if (navMenu.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking on a link
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.style.overflow = '';
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            const isClickInside = navMenu.contains(event.target) || mobileToggle.contains(event.target);
            if (!isClickInside && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Close menu on window resize to desktop
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768 && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }

    // ==========================================
    // Smooth Scrolling for Navigation Links
    // ==========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const headerOffset = 80;
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // ==========================================
    // Set Minimum Date for Appointment Booking
    // ==========================================
    const appointmentDateInput = document.getElementById('appointmentDate');
    if (appointmentDateInput) {
        // Set minimum date to tomorrow
        const today = new Date();
        today.setDate(today.getDate() + 1);
        const minDate = today.toISOString().split('T')[0];
        appointmentDateInput.setAttribute('min', minDate);
    }

    // ==========================================
    // Form Validation and Submission
    // ==========================================
    const appointmentForm = document.getElementById('appointmentForm');
    const formMessage = document.getElementById('formMessage');

    if (appointmentForm) {
        appointmentForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Clear previous messages
            formMessage.className = 'form-message';
            formMessage.textContent = '';
            formMessage.style.display = 'none';

            // Validate form
            if (!validateForm()) {
                return;
            }

            // Get form data
            const formData = new FormData(appointmentForm);

            // Show loading state
            const submitButton = appointmentForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Wird gesendet...';

            // Submit form via AJAX to Netlify
            fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams(formData).toString()
            })
            .then(response => {
                if (response.ok) {
                    // Success message
                    formMessage.className = 'form-message success';
                    formMessage.textContent = 'Vielen Dank! Ihre Terminanfrage wurde erfolgreich gesendet. Wir melden uns in Kürze bei Ihnen.';
                    formMessage.style.display = 'block';

                    // Reset form
                    appointmentForm.reset();

                    // Scroll to message
                    formMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    // Error message
                    formMessage.className = 'form-message error';
                    formMessage.textContent = 'Es ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut.';
                    formMessage.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                formMessage.className = 'form-message error';
                formMessage.textContent = 'Es ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut oder kontaktieren Sie uns telefonisch.';
                formMessage.style.display = 'block';
            })
            .finally(() => {
                // Restore button
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            });
        });
    }

    // ==========================================
    // Form Validation Function
    // ==========================================
    function validateForm() {
        let isValid = true;
        const requiredFields = appointmentForm.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            // Remove previous error styling
            field.style.borderColor = '';

            if (!field.value.trim()) {
                field.style.borderColor = '#dc3545';
                isValid = false;
            }

            // Email validation
            if (field.type === 'email' && field.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(field.value)) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                }
            }

            // Phone validation (basic)
            if (field.type === 'tel' && field.value) {
                const phoneRegex = /^[\d\s\+\-\(\)]+$/;
                if (!phoneRegex.test(field.value) || field.value.replace(/\D/g, '').length < 6) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                }
            }

            // Date validation (not in the past)
            if (field.type === 'date' && field.value) {
                const selectedDate = new Date(field.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);

                if (selectedDate < today) {
                    field.style.borderColor = '#dc3545';
                    isValid = false;
                    showError('Bitte wählen Sie ein Datum in der Zukunft.');
                }
            }
        });

        // Check privacy checkbox
        const privacyCheckbox = appointmentForm.querySelector('input[name="privacy"]');
        if (privacyCheckbox && !privacyCheckbox.checked) {
            isValid = false;
            showError('Bitte akzeptieren Sie die Datenschutzerklärung.');
        }

        if (!isValid) {
            showError('Bitte füllen Sie alle erforderlichen Felder korrekt aus.');
        }

        return isValid;
    }

    // ==========================================
    // Show Error Message
    // ==========================================
    function showError(message) {
        formMessage.className = 'form-message error';
        formMessage.textContent = message;
        formMessage.style.display = 'block';
        formMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // ==========================================
    // Reset field styling on input
    // ==========================================
    const formInputs = document.querySelectorAll('.appointment-form input, .appointment-form select, .appointment-form textarea');
    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.style.borderColor = '';
        });
    });

    // ==========================================
    // Highlight Active Navigation Link on Scroll
    // ==========================================
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-menu a[href^="#"]');

        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= (sectionTop - 100)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });

})();
