function initContactFormValidation() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    const fields = ['fullname', 'email', 'phone', 'message'].map(function (name) {
        return document.getElementById(`id_${name}`);
    }).filter(Boolean);
    const summary = document.getElementById('contact-form-feedback');
    const summaryTitle = document.getElementById('contact-form-summary-title');
    const summaryList = document.getElementById('contact-form-error-list');
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

    function updateSummary(showSummary) {
        if (!summary || !summaryList) return;

        const invalidFields = fields.filter(function (field) {
            return !validateField(field, false);
        });
        if (summaryTitle) {
            summaryTitle.textContent = invalidFields.length === 1
                ? 'Please review the highlighted field before sending.'
                : `Please review the ${invalidFields.length} highlighted fields before sending.`;
        }
        summaryList.replaceChildren();
        invalidFields.forEach(function (field) {
            const item = document.createElement('li');
            const link = document.createElement('a');
            link.href = `#${field.id}`;
            link.textContent = fieldLabels[field.name];
            item.appendChild(link);
            summaryList.appendChild(item);
        });
        summary.hidden = !showSummary || invalidFields.length === 0;
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

    updateSummary(showSummary);

    form.addEventListener('invalid', function (event) {
        const field = event.target;
        if (!fields.includes(field)) return;

        event.preventDefault();
        showSummary = true;
        validateField(field, true);
        updateSummary(showSummary);
    }, true);

    form.addEventListener('submit', function (event) {
        const valid = fields.map(function (field) {
            return validateField(field, true);
        }).every(Boolean);

        if (!valid) {
            event.preventDefault();
            showSummary = true;
            updateSummary(showSummary);
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
