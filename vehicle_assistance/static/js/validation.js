document.addEventListener('DOMContentLoaded', function () {
    var rules = {
        name: { min: 2, pattern: /^[a-zA-Z\s]+$/, message: 'Name: letters and spaces only' },
        email: { pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email' },
        phone: { pattern: /^[0-9]{10}$/, message: '10 digits required' },
        password: { min: 6, message: 'Minimum 6 characters' },
        otp: { pattern: /^[0-9]{6}$/, message: 'OTP must be 6 digits' },
    };

    function validateField(input) {
        if (!input) return true;

        var value = input.value.trim();
        var key = input.name || input.id;
        var rule = rules[key];

        if (input.hasAttribute('required') && !value) {
            window.setError(input, 'This field is required');
            return false;
        }

        if (!value) {
            window.setSuccess(input);
            return true;
        }

        if (rule) {
            if (rule.min && value.length < rule.min) {
                window.setError(input, rule.message);
                return false;
            }
            if (rule.pattern && !rule.pattern.test(value)) {
                window.setError(input, rule.message);
                return false;
            }
        }

        window.setSuccess(input);
        return true;
    }

    function validatePasswordMatch(passInput, confirmInput) {
        if (!passInput || !confirmInput || !confirmInput.value) return true;
        
        if (passInput.value !== confirmInput.value) {
            window.setError(confirmInput, 'Passwords do not match');
            return false;
        }
        window.setSuccess(confirmInput);
        return true;
    }

    function bindForm(formId, selector, extraCheck) {
        var form = document.getElementById(formId);
        if (!form) return;

        var fields = form.querySelectorAll(selector);
        
        fields.forEach(function(field) {
            field.addEventListener('blur', function () {
                validateField(this);
            });
        });

        form.addEventListener('submit', function (event) {
            var allValid = true;
            fields.forEach(function(field) {
                if (!validateField(field)) allValid = false;
            });
            if (extraCheck && !extraCheck()) allValid = false;

            if (!allValid) {
                event.preventDefault();
                var error = form.querySelector('.error');
                if (error) error.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    }

    function setupOtpInput() {
        var otp = document.getElementById('otp');
        if (!otp) return;
        otp.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 6);
        });
    }

    function setupBookingGps() {
        var button = document.getElementById('useCurrentLocation');
        var latInput = document.getElementById('latitude');
        var lngInput = document.getElementById('longitude');
        var status = document.getElementById('gpsStatus');
        var addressInput = document.getElementById('address');

        if (!button || !latInput || !lngInput) return;

        function setStatus(msg) {
            if (status) status.textContent = msg;
        }

        function buildAddress(addr) {
            var keys = ['house_number', 'road', 'town', 'city', 'state', 'postcode'];
            return keys.filter(function(k) { return addr && addr[k]; })
                      .map(function(k) { return addr[k]; }).join(', ');
        }

        button.addEventListener('click', async function () {
            if (!navigator.geolocation) {
                setStatus('GPS not supported');
                return;
            }

            button.disabled = true;
            button.textContent = 'Locating...';
            setStatus('Getting GPS...');

            try {
                var position = await new Promise(function (resolve, reject) {
                    navigator.geolocation.getCurrentPosition(resolve, reject, {
                        enableHighAccuracy: true,
                        timeout: 10000,
                    });
                });

                var lat = position.coords.latitude.toFixed(6);
                var lon = position.coords.longitude.toFixed(6);
                var accuracy = Math.round(position.coords.accuracy);

                latInput.value = lat;
                lngInput.value = lon;
                setStatus('GPS added (' + accuracy + 'm). Getting address...');

                var response = await fetch('/reverse-geo?lat=' + lat + '&lon=' + lon);
                var data = response.ok ? await response.json() : null;
                var addr = data && data.address ? buildAddress(data.address) : '';

                if (addr && addressInput) {
                    addressInput.value = addr;
                    setStatus('GPS added! Address filled.');
                } else {
                    setStatus('GPS added. Enter address manually.');
                }
            } catch (error) {
                setStatus('GPS failed. Enter address manually.');
            }

            button.disabled = false;
            button.textContent = 'Use Current Location (GPS)';
        });
    }

    function bindFormWithPassword(formId, selector) {
        bindForm(formId, selector, function () {
            var pass = document.querySelector('#' + formId + ' #password');
            var confirm = document.querySelector('#' + formId + ' #confirm_password');
            return validatePasswordMatch(pass, confirm);
        });
    }

    bindFormWithPassword('registerForm', 'input');
    bindForm('loginForm', 'input');
    bindForm('bookingForm', 'input, select, textarea');
    bindFormWithPassword('registerStaffForm', 'input, select, textarea');

    setupOtpInput();
    setupBookingGps();

    var style = document.createElement('style');
    style.textContent =
        'input.error,select.error,textarea.error{border-color:#ef476f!important;background-color:#fff5f5;}' +
        'input.success,select.success,textarea.success{border-color:#06d6a0!important;}' +
        '.error-message{color:#ef476f;font-size:.85rem;margin-top:5px;display:none;}';
    document.head.appendChild(style);
});
