/* ══════════════════════════════════════════
   SITE LOADER
══════════════════════════════════════════ */
(() => {
  const loader = document.getElementById('siteLoader');
  if (!loader) return;

  const MIN_VISIBLE = 900;   // ms — 讓滾輪動畫至少完整轉一輪，避免一閃即逝
  const MAX_WAIT     = 4000; // ms — 保底逾時，避免極端網路下卡住不放
  const start = Date.now();
  let done = false;

  function hideLoader() {
    if (done) return;
    done = true;
    const wait = Math.max(0, MIN_VISIBLE - (Date.now() - start));
    setTimeout(() => {
      loader.classList.add('is-hidden');
      document.body.classList.remove('is-loading');
    }, wait);
  }

  window.addEventListener('load', hideLoader);
  setTimeout(hideLoader, MAX_WAIT);
})();

/* ══════════════════════════════════════════
   NAV SCROLL STATE + HERO PARALLAX
══════════════════════════════════════════ */
const navbar      = document.getElementById('navbar');
const heroSection = document.querySelector('.hero-section');
const heroImg     = document.querySelector('.hero-img');

function onScroll() {
  const sy    = window.scrollY;
  const heroH = heroSection?.offsetHeight || window.innerHeight;
  const inHero = sy < heroH * 0.85;

  navbar.classList.toggle('on-dark',  inHero);
  navbar.classList.toggle('scrolled', !inHero && sy > 60);

  /* Hero parallax — translateY only; scale handled by CSS heroBreath animation */
  if (heroImg && sy < heroH * 1.1) {
    heroImg.style.transform = `translateY(${sy * 0.3}px)`;
  }
}

window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

/* ══════════════════════════════════════════
   HAMBURGER MENU
══════════════════════════════════════════ */
const hamburger  = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');

if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    mobileMenu.classList.toggle('open');
  });
  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.classList.remove('open');
      mobileMenu.classList.remove('open');
    });
  });
}

/* ══════════════════════════════════════════
   SMOOTH SCROLL
══════════════════════════════════════════ */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', e => {
    const id = anchor.getAttribute('href');
    if (id === '#') return;
    const target = document.querySelector(id);
    if (!target) return;
    e.preventDefault();
    const navH = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--nav-h')) || 64;
    window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - navH, behavior: 'smooth' });
  });
});

/* ══════════════════════════════════════════
   SCROLL FADE ANIMATIONS
══════════════════════════════════════════ */

/* Auto-tag section-level blocks that lack a fade class */
document.querySelectorAll(
  '.section-header, .split-text, .bridge-h2, .bridge-eyebrow, ' +
  '.subsidy-block, .area-info, .map-visual, .phi-header'
).forEach(el => {
  if (!el.classList.contains('fade-in')) el.classList.add('fade-up');
});

const scrollObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      scrollObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.05, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.fade-in, .fade-up').forEach(el => scrollObserver.observe(el));

/* ══════════════════════════════════════════
   CURSOR STAR TRAIL
══════════════════════════════════════════ */
const STARS = ['✦', '✧', '⋆', '·', '✦'];
let lastStarTime = 0;

document.addEventListener('mousemove', e => {
  const now = Date.now();
  if (now - lastStarTime < 40) return;   // throttle: max ~25 stars/sec
  lastStarTime = now;

  const el = document.createElement('span');
  el.className = 'cursor-star';
  el.textContent = STARS[Math.floor(Math.random() * STARS.length)];

  const size = 10 + Math.random() * 10;           // 10–20px
  const dx   = (Math.random() - 0.5) * 18;        // slight scatter
  const dy   = -(18 + Math.random() * 18);         // float upward

  el.style.cssText = `
    left: ${e.clientX}px;
    top:  ${e.clientY}px;
    font-size: ${size}px;
    --dx: ${dx}px;
    --dy: ${dy}px;
  `;

  document.body.appendChild(el);
  el.addEventListener('animationend', () => el.remove(), { once: true });
});

/* ══════════════════════════════════════════
   DARK QUOTE WORD REVEAL
══════════════════════════════════════════ */
const darkQuoteSection = document.querySelector('.dark-quote-section');
if (darkQuoteSection) {
  const quoteObserver = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
      darkQuoteSection.classList.add('revealed');
      quoteObserver.disconnect();
    }
  }, { threshold: 0.5 });
  quoteObserver.observe(darkQuoteSection);
}
