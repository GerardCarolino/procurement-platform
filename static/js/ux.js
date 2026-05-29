/* ── ProcureGov UX Enhancements ───────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {

  // ── 1. Page fade-in ───────────────────────────────────────────────────────
  document.body.classList.add('pg-fade-in');


  // ── 2. Navbar scroll shadow ───────────────────────────────────────────────
  const navbar = document.querySelector('.pg-navbar');
  if (navbar) {
    const onScroll = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }


  // ── 3. Scroll-triggered card animations ───────────────────────────────────
  // Add pg-slide-up to proc-cards and widget-cards automatically
  document.querySelectorAll('.proc-card, .widget-card').forEach((el, i) => {
    el.classList.add('pg-slide-up');
    el.style.transitionDelay = `${Math.min(i * 40, 300)}ms`;
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.pg-slide-up').forEach(el => observer.observe(el));


  // ── 4. Button loading spinner on form submit ───────────────────────────────
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('[type="submit"]');
      if (!btn || btn.dataset.noLoading) return;

      // Wrap text in span if not already
      if (!btn.querySelector('.btn-text')) {
        btn.innerHTML = `<span class="btn-text">${btn.innerHTML}</span>`;
      }
      btn.classList.add('btn-loading');

      // Safety fallback — re-enable after 8s in case of error
      setTimeout(() => btn.classList.remove('btn-loading'), 8000);
    });
  });


  // ── 5. Toast notifications (replaces Django messages banner) ──────────────
  // Create container
  const toastContainer = document.createElement('div');
  toastContainer.id = 'pg-toast-container';
  document.body.appendChild(toastContainer);

  function showToast(message, type = 'info') {
    const icons = {
      success: 'bi-check-circle-fill',
      error:   'bi-x-circle-fill',
      warning: 'bi-exclamation-triangle-fill',
      info:    'bi-info-circle-fill',
    };
    const toast = document.createElement('div');
    toast.className = `pg-toast toast-${type}`;
    toast.innerHTML = `
      <i class="bi ${icons[type] || icons.info}" style="font-size:1rem;flex-shrink:0;"></i>
      <span>${message}</span>
    `;
    toastContainer.appendChild(toast);

    // Auto-dismiss after 4s
    setTimeout(() => {
      toast.classList.add('toast-out');
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // Convert existing Django messages to toasts
  document.querySelectorAll('.messages-container [data-message]').forEach(el => {
    const message = el.dataset.message;
    const tags    = el.dataset.tags || 'info';
    const type    = tags.includes('error')   ? 'error'
                  : tags.includes('warning') ? 'warning'
                  : tags.includes('success') ? 'success'
                  : 'info';
    showToast(message, type);
    el.remove();
  });

  // Expose globally so templates can call it
  window.pgToast = showToast;


  // ── 6. Auto-dismiss alert banners (fallback for non-toast alerts) ──────────
  document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .4s ease, max-height .4s ease';
      alert.style.opacity = '0';
      alert.style.maxHeight = '0';
      alert.style.overflow = 'hidden';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });


  // ── 7. Confirm dangerous actions (extra safety on delete buttons) ──────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

});