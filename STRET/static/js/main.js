/* ═══════════════════════════════════════
   STRET — main.js
   Frontend interactions
═══════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  // ─── Sidebar Toggle ───────────────────
  const sidebar       = document.getElementById('sidebar');
  const overlay       = document.getElementById('sidebarOverlay');
  const toggleBtn     = document.getElementById('sidebarToggle');
  const closeBtn      = document.getElementById('sidebarToggleClose');

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  if (toggleBtn) toggleBtn.addEventListener('click', openSidebar);
  if (closeBtn)  closeBtn.addEventListener('click',  closeSidebar);
  if (overlay)   overlay.addEventListener('click',   closeSidebar);

  // ─── Auto-dismiss Alerts ─────────────
  setTimeout(() => {
    document.querySelectorAll('.custom-alert').forEach(el => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    });
  }, 5000);

  // ─── Animate Stat Values ─────────────
  document.querySelectorAll('.stat-value').forEach(el => {
    const text = el.textContent.trim();
    const num = parseFloat(text.replace(/[^0-9.]/g, ''));
    if (!isNaN(num) && num > 0 && num < 100000) {
      let start = 0;
      const duration = 900;
      const step = (timestamp) => {
        if (!start) start = timestamp;
        const progress = Math.min((timestamp - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = Math.floor(eased * num);
        el.textContent = text.includes('.') ? current.toFixed(0) : current;
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = text;  // restore exact
      };
      requestAnimationFrame(step);
    }
  });

  // ─── Animated Metric Bars ─────────────
  document.querySelectorAll('.metric-bar-fill').forEach(el => {
    const targetWidth = el.style.width;
    el.style.width = '0%';
    setTimeout(() => { el.style.width = targetWidth; }, 300);
  });

  // ─── Distribution bars animation ─────
  document.querySelectorAll('.dist-bar-fill').forEach(el => {
    const w = el.style.width;
    el.style.width = '0%';
    setTimeout(() => { el.style.width = w; }, 400);
  });

  // ─── Table Row Hover Effect ───────────
  document.querySelectorAll('.table-dark-custom tbody tr').forEach(tr => {
    tr.addEventListener('mouseenter', () => {
      tr.style.background = 'rgba(79,142,247,0.04)';
    });
    tr.addEventListener('mouseleave', () => {
      tr.style.background = '';
    });
  });

  // ─── Chart Image Lightbox (click to enlarge) ──
  document.querySelectorAll('.chart-img').forEach(img => {
    img.style.cursor = 'zoom-in';
    img.addEventListener('click', () => {
      const overlay = document.createElement('div');
      overlay.style.cssText = `
        position:fixed;inset:0;background:rgba(0,0,0,0.92);
        display:flex;align-items:center;justify-content:center;
        z-index:9999;cursor:zoom-out;padding:20px;
      `;
      const imgEl = document.createElement('img');
      imgEl.src = img.src;
      imgEl.style.cssText = `max-width:95vw;max-height:90vh;border-radius:10px;object-fit:contain;box-shadow:0 20px 60px rgba(0,0,0,0.5);`;
      overlay.appendChild(imgEl);
      overlay.addEventListener('click', () => document.body.removeChild(overlay));
      document.body.appendChild(overlay);
    });
  });

  // ─── Form select style fix ──────────
  document.querySelectorAll('.form-select-dark').forEach(sel => {
    sel.style.backgroundColor = 'var(--bg-primary)';
    sel.style.color = 'var(--text-primary)';
    sel.addEventListener('change', () => {
      sel.style.color = 'var(--text-primary)';
    });
  });

  console.log('%cSTRET Clustering System', 'color:#4F8EF7;font-size:16px;font-weight:800;');
  console.log('%cK-Means & Fuzzy C-Means | Sudut Kota Lama', 'color:#8A93B0;font-size:12px;');
});
