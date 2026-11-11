function initContactFormValidation() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    const fields = ['fullname', 'email', 'phone', 'message'].map(function (name) {
        return document.getElementById(`id_${name}`);
    }).filter(Boolean);
    const summary = document.getElementById('contact-form-feedback');

    function getError(field) {
        const value = field.value.trim();
        if (!value) return 'This field is required.';

        if (field.id === 'id_fullname' && value.length < 2) {
            return 'Please enter a name with at least 2 characters.';
        }
        if (field.id === 'id_email' && field.validity.typeMismatch) {
            return 'Enter a valid email address.';
        }
        if (field.id === 'id_phone') {
            const digits = value.replace(/\D/g, '');
            if (!/^\+?[\d\s().-]+$/.test(value) || digits.length < 7 || digits.length > 15) {
                return 'Enter a valid phone number with 7 to 15 digits.';
            }
        }
        if (field.id === 'id_message' && value.length > 5000) {
            return 'Your message must be 5000 characters or fewer.';
        }
        return '';
    }

    function validateField(field, showFeedback) {
        const error = getError(field);
        const feedback = document.getElementById(`${field.name}-feedback`);
        const serverErrors = document.getElementById(`${field.name}-server-errors`);

        field.setCustomValidity(error);
        if (showFeedback) {
            field.classList.toggle('is-invalid', Boolean(error));
            field.setAttribute('aria-invalid', String(Boolean(error)));
            if (feedback) feedback.textContent = error;
            if (serverErrors && error) serverErrors.hidden = true;
        }
        return !error && field.validity.valid;
    }

    function updateSummary() {
        if (summary) {
            summary.hidden = fields.every(function (field) {
                return field.validity.valid;
            });
        }
    }

    fields.forEach(function (field) {
        const serverErrors = document.getElementById(`${field.name}-server-errors`);
        const hasServerError = serverErrors && !serverErrors.hidden;
        if (hasServerError) {
            field.classList.add('is-invalid');
            field.setAttribute('aria-invalid', 'true');
        }
        validateField(field, Boolean(hasServerError));

        field.addEventListener('input', function () {
            if (serverErrors) serverErrors.hidden = true;
            validateField(field, true);
            updateSummary();
        });
        field.addEventListener('blur', function () {
            validateField(field, true);
            updateSummary();
        });
    });

    form.addEventListener('invalid', function (event) {
        const field = event.target;
        if (!fields.includes(field)) return;

        event.preventDefault();
        validateField(field, true);
        if (summary) summary.hidden = false;
    }, true);

    form.addEventListener('submit', function (event) {
        const valid = fields.map(function (field) {
            return validateField(field, true);
        }).every(Boolean);

        if (!valid) {
            event.preventDefault();
            if (summary) summary.hidden = false;
            const firstInvalid = fields.find(function (field) {
                return !field.validity.valid;
            });
            if (firstInvalid) firstInvalid.focus();
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initContactFormValidation, { once: true });
} else {
    initContactFormValidation();
}
