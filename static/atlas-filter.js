/* Lightweight progressive enhancement for the public gravity instrument atlas. */
(() => {
  'use strict';
  const form = document.getElementById('atlas-filter');
  const count = document.getElementById('visible-instrument-count');
  const cards = [...document.querySelectorAll('#instrument-card-grid [data-measurement][data-sensing]')];
  const rows = [...document.querySelectorAll('.comparison-matrix tbody [data-measurement][data-sensing]')];
  if (!form || !count || !cards.length) return;
  function applyFilters() {
    const measurement = form.elements.measurement.value;
    const sensing = form.elements.sensing.value;
    const show = (el) => (measurement === 'all' || el.dataset.measurement === measurement)
      && (sensing === 'all' || el.dataset.sensing === sensing);
    let shown = 0;
    for (const card of cards) { const visible = show(card); card.hidden = !visible; if (visible) shown++; }
    for (const row of rows) row.hidden = !show(row);
    count.textContent = String(shown);
  }
  form.addEventListener('change', applyFilters);
  form.querySelector('.facet-reset').addEventListener('click', () => {
    form.elements.measurement.value = 'all';
    form.elements.sensing.value = 'all';
    applyFilters();
  });
  applyFilters();
})();
