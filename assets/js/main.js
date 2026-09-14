(function () {
  'use strict';

  // ── Nav: light-on-dark over the dark banner, solid light past it ──
  // Every page opens with a dark band (hero or page header). The two states are
  // mutually exclusive: `on-dark` is white text, `scrolled` is a light backdrop,
  // so applying both at once renders the nav invisible.
  const header = document.getElementById('site-header');
  // Any full-width dark band at the top of a page. A layout that introduces a
  // new one MUST be added here, or the nav strips `on-dark` and renders light
  // text on a light background — this has been missed three times now.
  const DARK_BANNERS = '.hero, .page-header, .member-hero, .topic-hero';
  const darkBanner = document.querySelector(DARK_BANNERS);

  function updateNav() {
    if (!header) return;
    // Measured, not hardcoded — $nav-height lives in SCSS and has changed before
    const navHeight = header.offsetHeight || 80;
    const overDark = darkBanner
      ? darkBanner.getBoundingClientRect().bottom > navHeight
      : false;

    header.classList.toggle('on-dark', overDark);
    header.classList.toggle('scrolled', !overDark && window.scrollY > 20);
  }

  window.addEventListener('scroll', updateNav, { passive: true });
  updateNav();

  // ── Mobile nav toggle ─────────────────────────────
  const toggle = document.querySelector('.nav-toggle');
  const mobileNav = document.getElementById('nav-mobile');
  const scrim = document.getElementById('nav-scrim');

  function setMenu(open) {
    if (!toggle || !mobileNav) return;
    toggle.classList.toggle('open', open);
    mobileNav.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', open);
    // Header goes solid so it never sits transparent over the open menu
    if (header) header.classList.toggle('menu-open', open);
    if (scrim) {
      scrim.hidden = false;
      scrim.classList.toggle('open', open);
    }
    document.body.style.overflow = open ? 'hidden' : '';
  }

  if (toggle && mobileNav) {
    toggle.addEventListener('click', function () {
      setMenu(!toggle.classList.contains('open'));
    });

    // Dismiss on scrim tap, link tap, or Escape
    if (scrim) scrim.addEventListener('click', function () { setMenu(false); });

    mobileNav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { setMenu(false); });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setMenu(false);
    });

    // Returning to desktop width must not leave the body scroll-locked
    window.addEventListener('resize', function () {
      if (window.innerWidth > 768 && toggle.classList.contains('open')) setMenu(false);
    });
  }

  // ── Team filter ───────────────────────────────────
  const filterBtns = document.querySelectorAll('.filter-btn');
  const memberCards = document.querySelectorAll('.member-card');

  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const filter = btn.dataset.filter;

      filterBtns.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');

      memberCards.forEach(function (card) {
        const types = (card.dataset.types || '').split(',');
        const show = filter === 'all' || types.includes(filter);
        card.style.display = show ? '' : 'none';
      });
    });
  });

  // ── Reveal on scroll ──────────────────────────────
  const reveals = document.querySelectorAll('.reveal');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    reveals.forEach(function (el) { observer.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('visible'); });
  }

  // ── BibTeX show/hide ──────────────────────────────
  document.querySelectorAll('.pub-cite-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const pre = document.getElementById(btn.dataset.target);
      if (!pre) return;
      const open = pre.hidden;
      pre.hidden = !open;
      btn.setAttribute('aria-expanded', open);
      btn.classList.toggle('active', open);
    });
  });

  // ── Video fallback ────────────────────────────────
  const video = document.querySelector('.hero-video');
  if (video) {
    video.addEventListener('error', function () {
      video.style.display = 'none';
    });
  }
}());
