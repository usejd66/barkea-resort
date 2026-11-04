function initVillaFilters() {
    const form = document.getElementById('villa-filter');
    if (!form) return;

    const cards = Array.from(document.querySelectorAll('[data-villa]'));
    const noResults = document.getElementById('no-results');
    const filters = {
        area: document.getElementById('filter-area'),
        floors: document.getElementById('filter-floors'),
        type: document.getElementById('filter-type'),
    };

    function applyFilters() {
        let visibleCount = 0;
        cards.forEach(function (card) {
            const matches = Object.entries(filters).every(function ([key, filter]) {
                return !filter || !filter.value || card.dataset[key] === filter.value;
            });
            card.hidden = !matches;
            if (matches) visibleCount += 1;
        });

        if (noResults) noResults.hidden = visibleCount > 0;
    }

    Object.values(filters).forEach(function (filter) {
        if (filter) filter.addEventListener('change', applyFilters);
    });
    form.addEventListener('reset', function () {
        window.requestAnimationFrame(applyFilters);
    });
}

function initGalleryFilters() {
    const filterGroup = document.getElementById('gallery-filters');
    const grid = document.getElementById('gallery-grid');
    if (!filterGroup || !grid) return;

    const buttons = Array.from(filterGroup.querySelectorAll('[data-filter]'));
    const items = Array.from(grid.querySelectorAll('[data-gallery-item]'));
    const results = document.getElementById('gallery-results');

    function applyFilter(activeButton) {
        const category = activeButton.dataset.filter;
        let visibleCount = 0;

        buttons.forEach(function (button) {
            const active = button === activeButton;
            button.classList.toggle('btn-primary', active);
            button.classList.toggle('btn-outline-secondary', !active);
            button.setAttribute('aria-pressed', String(active));
        });

        items.forEach(function (item) {
            const visible = category === 'all' || item.dataset.category === category;
            item.hidden = !visible;
            if (visible) visibleCount += 1;
        });

        if (results) {
            const categoryLabel = activeButton.textContent.trim();
            results.textContent = category === 'all'
                ? `Showing all ${visibleCount} photos.`
                : `Showing ${visibleCount} ${categoryLabel.toLowerCase()} photos.`;
        }
    }

    filterGroup.addEventListener('click', function (event) {
        const button = event.target.closest('[data-filter]');
        if (button && filterGroup.contains(button)) applyFilter(button);
    });
}

function initGalleryLightbox() {
    const grid = document.getElementById('gallery-grid');
    const dialog = document.getElementById('gallery-lightbox');
    if (!grid || !dialog || typeof dialog.showModal !== 'function') return;

    const image = document.getElementById('lightbox-image');
    const caption = document.getElementById('lightbox-caption');
    const position = document.getElementById('lightbox-position');
    const closeButton = dialog.querySelector('[data-lightbox-close]');
    const previousButton = dialog.querySelector('[data-lightbox-previous]');
    const nextButton = dialog.querySelector('[data-lightbox-next]');
    let activeImages = [];
    let activeIndex = 0;
    let returnFocus = null;

    function getVisibleImages() {
        return Array.from(grid.querySelectorAll('[data-gallery-open]')).filter(function (button) {
            return !button.closest('[data-gallery-item]').hidden;
        });
    }

    function showImage() {
        const trigger = activeImages[activeIndex];
        if (!trigger) return;

        image.src = trigger.dataset.galleryFull;
        image.alt = trigger.dataset.galleryAlt;
        caption.textContent = trigger.dataset.galleryCaption;
        position.textContent = `${activeIndex + 1} / ${activeImages.length}`;
        previousButton.hidden = activeImages.length < 2;
        nextButton.hidden = activeImages.length < 2;
    }

    function moveImage(direction) {
        if (activeImages.length < 2) return;
        activeIndex = (activeIndex + direction + activeImages.length) % activeImages.length;
        showImage();
    }

    grid.addEventListener('click', function (event) {
        const trigger = event.target.closest('[data-gallery-open]');
        if (!trigger || !grid.contains(trigger)) return;

        activeImages = getVisibleImages();
        activeIndex = activeImages.indexOf(trigger);
        returnFocus = trigger;
        showImage();
        dialog.showModal();
        closeButton.focus();
    });

    previousButton.addEventListener('click', function () {
        moveImage(-1);
    });
    nextButton.addEventListener('click', function () {
        moveImage(1);
    });
    closeButton.addEventListener('click', function () {
        dialog.close();
    });
    dialog.addEventListener('click', function (event) {
        if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener('keydown', function (event) {
        if (event.key === 'ArrowLeft') {
            event.preventDefault();
            moveImage(-1);
        } else if (event.key === 'ArrowRight') {
            event.preventDefault();
            moveImage(1);
        }
    });
    dialog.addEventListener('close', function () {
        image.removeAttribute('src');
        activeImages = [];
        if (returnFocus) returnFocus.focus();
        returnFocus = null;
    });
}

function initMobileNavigation() {
    const navigation = document.getElementById('mainNavbar');
    if (!navigation || !window.bootstrap) return;

    const collapse = window.bootstrap.Collapse.getOrCreateInstance(navigation, { toggle: false });
    navigation.addEventListener('click', function (event) {
        const link = event.target.closest('a[href]');
        if (link && window.matchMedia('(max-width: 991.98px)').matches) {
            collapse.hide();
        }
    });
}

function initSiteInteractions() {
    initVillaFilters();
    initGalleryFilters();
    initGalleryLightbox();
    initMobileNavigation();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSiteInteractions, { once: true });
} else {
    initSiteInteractions();
}
