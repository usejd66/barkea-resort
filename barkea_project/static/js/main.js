document.addEventListener('DOMContentLoaded', function () {

    // ---- Villas filter ----
    const villaForm = document.getElementById('villa-filter');
    if (villaForm) {
        const cards = document.querySelectorAll('[data-villa]');
        const noResults = document.getElementById('no-results');
        const area = document.getElementById('filter-area');
        const floors = document.getElementById('filter-floors');
        const type = document.getElementById('filter-type');

        function applyVillaFilter() {
            let visible = 0;
            cards.forEach(function (card) {
                const ok =
                    (!area.value || card.dataset.area === area.value) &&
                    (!floors.value || card.dataset.floors === floors.value) &&
                    (!type.value || card.dataset.type === type.value);
                card.classList.toggle('d-none', !ok);
                if (ok) visible++;
            });
            noResults.classList.toggle('d-none', visible !== 0);
        }

        [area, floors, type].forEach(function (el) {
            el.addEventListener('change', applyVillaFilter);
        });
        villaForm.addEventListener('reset', function () {
            setTimeout(applyVillaFilter, 0);
        });
    }

    // ---- Gallery filter ----
    const filterBox = document.getElementById('gallery-filters');
    if (filterBox) {
        const buttons = filterBox.querySelectorAll('[data-filter]');
        const items = document.querySelectorAll('[data-category]');
        const carouselSection = document.getElementById('gallery-carousel-section');

        buttons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                const f = btn.dataset.filter;
                buttons.forEach(function (b) {
                    b.classList.toggle('btn-primary', b === btn);
                    b.classList.toggle('btn-outline-secondary', b !== btn);
                    b.setAttribute('aria-pressed', String(b === btn));
                });
                items.forEach(function (item) {
                    item.classList.toggle('d-none', f !== 'all' && item.dataset.category !== f);
                });
                if (carouselSection) {
                    carouselSection.classList.toggle('d-none', f !== 'all');
                }
            });
        });
    }
});