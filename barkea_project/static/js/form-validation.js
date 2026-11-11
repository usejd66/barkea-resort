function initContactFormValidation() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    const fields = ['fullname', 'email', 'phone', 'message'].map(function (name) {
        return document.getElementById(`id_${name}`);
    }).filter(Boolean);
    const summary = document.getElementById('contact-form-feedback');
    const summaryTitle = document.getElementById('contact-form-summary-title');
    const summaryList = document.getElementById('contact-form-error-list');
    let summaryToast;
    const fieldLabels = {
        fullname: 'Full name',
        email: 'Email',
        phone: 'Phone',
        message: 'Message',
    };

    function getError(field) {
        const value = field.value.trim();
        if (!value) {
            return {
                id_fullname: 'Enter your full name.',
                id_email: 'Enter your email address.',
                id_phone: 'Enter your phone number.',
                id_message: 'Enter a message.',
            }[field.id];
        }

        if (field.id === 'id_fullname' && value.length < 2) {
            return 'Enter at least 2 characters for your name.';
        }
        if (field.id === 'id_fullname' && !/^\p{L}[\p{L}\p{M}]*(?:[\s.'’-]\p{L}[\p{L}\p{M}.]*)*$/u.test(value)) {
            return 'Use letters only; spaces, hyphens, apostrophes and periods are allowed.';
        }
        if (field.id === 'id_email' && field.validity.typeMismatch) {
            return 'Enter a valid email address.';
        }
        if (field.id === 'id_phone') {
            const digits = value.replace(/\D/g, '');
            if (!/^\+?[\d\s().-]+$/.test(value) || digits.length < 7 || digits.length > 15) {
                return 'Enter a valid phone number (7-15 digits).';
            }
        }
        if (field.id === 'id_message' && value.length < 10) {
            return 'Please add a little more detail (at least 10 characters).';
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
        const serverError = serverErrors && !serverErrors.hidden
            ? serverErrors.textContent.trim()
            : '';
        const message = error || serverError;

        field.setCustomValidity(message);
        if (showFeedback) {
            field.classList.toggle('is-invalid', Boolean(message));
            field.setAttribute('aria-invalid', String(Boolean(message)));
            if (feedback) feedback.textContent = error;
            if (serverErrors && error) serverErrors.hidden = true;
        }
        return !message && field.validity.valid;
    }

    function getFieldError(field) {
        const clientError = getError(field);
        if (clientError) return clientError;

        const serverErrors = document.getElementById(`${field.name}-server-errors`);
        return serverErrors ? serverErrors.textContent.trim() : '';
    }

    function updateSummary(announce) {
        if (!summary || !summaryList) return;

        const invalidFields = fields.filter(function (field) {
            return !validateField(field, false);
        });
        if (summaryTitle) {
            summaryTitle.textContent = invalidFields.length === 1
                ? "Your message wasn't sent. Please correct this field and try again:"
                : `Your message wasn't sent. Please correct these ${invalidFields.length} fields and try again:`;
        }
        summaryList.replaceChildren();
        invalidFields.forEach(function (field) {
            const item = document.createElement('li');
            const link = document.createElement('a');
            link.href = `#${field.id}`;
            link.textContent = `${fieldLabels[field.name]} — ${getFieldError(field)}`;
            item.appendChild(link);
            summaryList.appendChild(item);
        });

        if (invalidFields.length === 0) {
            if (summaryToast) {
                summaryToast.hide();
            } else {
                summary.hidden = true;
            }
        } else if (announce) {
            summary.hidden = false;
            if (window.bootstrap && window.bootstrap.Toast) {
                summaryToast = window.bootstrap.Toast.getOrCreateInstance(summary);
                summaryToast.show();
            }
        }
    }

    let showSummary = false;
    fields.forEach(function (field) {
        const serverErrors = document.getElementById(`${field.name}-server-errors`);
        const hasServerError = serverErrors && !serverErrors.hidden;
        if (hasServerError) showSummary = true;
        validateField(field, Boolean(hasServerError));

        field.addEventListener('input', function () {
            if (serverErrors) serverErrors.hidden = true;
            validateField(field, true);
            updateSummary(showSummary);
        });
        field.addEventListener('blur', function () {
            validateField(field, true);
            updateSummary(showSummary);
        });
    });

    summary.addEventListener('hidden.bs.toast', function () {
        summary.hidden = true;
    });
    updateSummary(showSummary);

    form.addEventListener('invalid', function (event) {
        const field = event.target;
        if (!fields.includes(field)) return;

        event.preventDefault();
        validateField(field, true);
        updateSummary(true);
    }, true);

    form.addEventListener('submit', function (event) {
        const valid = fields.map(function (field) {
            return validateField(field, true);
        }).every(Boolean);

        if (!valid) {
            event.preventDefault();
            updateSummary(true);
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
