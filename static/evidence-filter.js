/* Progressive enhancement; evidence remains available as static HTML without JS. */
(() => {
  'use strict';
  const filter = document.getElementById('evidence-filter');
  const count = document.getElementById('visible-evidence-count');
  const records = [...document.querySelectorAll('#evidence-list [data-evidence-id]')];
  if (!filter || !count || !records.length) return;
  const appControl = document.getElementById('evidence-application');
  const statusControl = document.getElementById('evidence-status');
  function update() {
    const app = appControl.value, status = statusControl.value;
    let visible = 0;
    for (const record of records) {
      const apps = record.dataset.applications.split(',');
      const show = (app === 'all' || apps.includes(app)) && (status === 'all' || record.dataset.status === status);
      record.hidden = !show;
      if (show) visible++;
    }
    count.textContent = String(visible);
  }
  filter.addEventListener('change', update);
  document.getElementById('evidence-reset').addEventListener('click', () => {
    appControl.value = 'all'; statusControl.value = 'all'; update();
  });
  for (const anchor of document.querySelectorAll('[data-application-jump]')) {
    anchor.addEventListener('click', () => { appControl.value = anchor.dataset.applicationJump; statusControl.value = 'all'; update(); });
  }
  update();
})();
