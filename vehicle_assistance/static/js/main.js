document.addEventListener('DOMContentLoaded', function () {
    setupActiveNav();
    setupMobileNav();
    setupAlerts();
    setupFormButtons();
    setupInputHelpers();
    setupConfirmPrompts();
    setupQuickSearch();
});

function setupActiveNav() {
    var path = window.location.pathname;
    document.querySelectorAll('.nav-menu a').forEach(function(link) {
        var href = link.getAttribute('href') || '';
        var active = (href === '/' && path === '/') || (href !== '/' && path.indexOf(href) === 0);
        link.classList.toggle('active', active);
    });
}

function setupMobileNav() {
    var toggle = document.querySelector('.nav-toggle');
    var menu = document.querySelector('.nav-menu');
    if (!toggle || !menu) return;

    toggle.addEventListener('click', function (event) {
        event.stopPropagation();
        menu.classList.toggle('active');
    });

    document.addEventListener('click', function (event) {
        if (!toggle.contains(event.target) && !menu.contains(event.target)) {
            menu.classList.remove('active');
        }
    });

    menu.querySelectorAll('a').forEach(function(link) {
        link.addEventListener('click', function () {
            menu.classList.remove('active');
        });
    });
}

function setupAlerts() {
    document.querySelectorAll('.close-alert').forEach(function(btn) {
        btn.addEventListener('click', function () {
            var alert = this.closest('.alert');
            if (alert) alert.remove();
        });
    });

    document.querySelectorAll('.alert').forEach(function(box) {
        setTimeout(function () {
            if (box.parentElement) box.remove();
        }, 5000);
    });
}

function setupFormButtons() {
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function () {
            var btn = this.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.textContent = 'Processing...';
            }
        });
    });
}

function setupInputHelpers() {
    var today = new Date().toISOString().split('T')[0];

    document.querySelectorAll('input[type="date"]').forEach(function(input) {
        if (!input.hasAttribute('min')) input.setAttribute('min', today);
    });

    document.querySelectorAll('input[type="tel"]').forEach(function(input) {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
        });
    });

    document.querySelectorAll('.password-toggle').forEach(function(btn) {
        btn.addEventListener('click', function () {
            var input = this.previousElementSibling;
            if (!input) return;
            var isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            this.textContent = isPassword ? 'Hide' : 'Show';
        });
    });

    document.querySelectorAll('a[href^="#"]').forEach(function(link) {
        link.addEventListener('click', function (event) {
            var href = this.getAttribute('href');
            var target = document.querySelector(href);
            if (target && href && href !== '#') {
                event.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

function setupConfirmPrompts() {
    document.querySelectorAll('[data-confirm]').forEach(function(el) {
        var eventType = el.tagName === 'FORM' ? 'submit' : 'click';
        el.addEventListener(eventType, function (event) {
            if (!window.confirm(this.getAttribute('data-confirm') || 'Are you sure?')) {
                event.preventDefault();
            }
        });
    });
}

function setupQuickSearch() {
    document.querySelectorAll('[data-search-target]').forEach(function(input) {
        var target = document.querySelector(input.getAttribute('data-search-target'));
        if (!target) return;

        input.addEventListener('input', function () {
            var query = this.value.toLowerCase().trim();
            target.querySelectorAll('[data-search-item], tr, .booking-card').forEach(function(item) {
                item.style.display = (item.textContent || '').toLowerCase().indexOf(query) !== -1 ? '' : 'none';
            });
        });
    });
}

function getGroupError(input) {
    var group = input.closest('.form-group');
    return group ? group.querySelector('.error-message') : null;
}

window.setError = function (input, message) {
    if (!input) return;
    var error = getGroupError(input);
    input.classList.add('error');
    input.classList.remove('success');
    if (error) {
        error.textContent = message;
        error.style.display = 'block';
    }
};

window.setSuccess = function (input) {
    if (!input) return;
    var error = getGroupError(input);
    input.classList.remove('error');
    input.classList.add('success');
    if (error) {
        error.textContent = '';
        error.style.display = 'none';
    }
};
