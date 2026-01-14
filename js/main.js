// Data loaded from data.js

// Helper: Get concise date string (e.g., "JAN 13 • 2026")
const getFormattedDate = () => {
  const date = new Date();
  const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
  return `${months[date.getMonth()]} ${date.getDate()} • ${date.getFullYear()}`;
};

function createBentoCard(item, category) {
  const card = document.createElement('div');
  card.className = `bento-card ${item.layout || 'regular'}`;
  card.dataset.id = item.id; // Store ID for click handler

  // Note: Date removed from here, moved to Hero.
  // Context quote remains.
  card.innerHTML = `
    <img src="${item.image}" alt="${item.title}" class="card-image" loading="lazy">
    <div class="card-overlay">
      <div class="card-context" style="color: #ddd; font-family: var(--font-lit); font-style: italic; font-size: 0.85rem; margin-bottom: 0.8rem; line-height: 1.4; opacity: 0.9;">
            ${item.dailyContext || "Art for today."}
      </div>
      <h3 class="card-title">${item.title}</h3>
      <div class="card-subtitle">${item.subtitle}</div>
    </div>
  `;

  // Add Click Event
  card.addEventListener('click', () => openModal(item, category));

  return card;
}

function renderGrid(items, containerId, category) {
  const container = document.getElementById(containerId);
  container.innerHTML = ''; // Clear container to be safe
  items.forEach((item, index) => {
    const card = createBentoCard(item, category);
    card.style.animationDelay = `${index * 0.1}s`;
    container.appendChild(card);
  });
}

// Modal Logic
function openModal(item, category) {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay active'; // Start active for now, triggering transition next
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <img src="${item.image}" alt="${item.title}" class="modal-banner-image">
        <button class="modal-close">×</button>
      </div>
      <div class="modal-body">
        <div class="modal-category">${category}</div>
        <h2 class="modal-title">${item.title}</h2>
        <div class="modal-subtitle">${item.subtitle}</div>

        <div class="modal-significance">
          ${item.significance}
        </div>

        <div class="modal-section" style="margin-top: 2rem; border-top: 1px dashed #333; padding-top: 1.5rem;">
          <span class="modal-label" style="color: var(--accent-gold);">The Technician's View</span>
          <p class="modal-text">${item.technicianReview}</p>
        </div>

        <div class="modal-section" style="background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 12px; margin-top: 1.5rem;">
          <span class="modal-label" style="color: #bbb; display: block; margin-bottom: 0.5rem; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Artist Story</span>
          <p class="modal-text" style="font-style: italic; color: #eee;">${item.artistFact}</p>
        </div>

        <div class="quote-block">
          "${item.soulNote}"
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Close handler
  const closeBtn = modal.querySelector('.modal-close');
  closeBtn.addEventListener('click', () => {
    modal.classList.remove('active');
    setTimeout(() => modal.remove(), 400); // Wait for transition
  });

  // Close on outside click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.classList.remove('active');
      setTimeout(() => modal.remove(), 400);
    }
  });
}

// Scroll Animation
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

function initAnimations() {
  document.querySelectorAll('.bento-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
  });
}

// Custom Cursor Logic
function initCursor() {
  const cursorDot = document.createElement('div');
  cursorDot.className = 'cursor-dot';

  const cursorOutline = document.createElement('div');
  cursorOutline.className = 'cursor-outline';

  document.body.appendChild(cursorDot);
  document.body.appendChild(cursorOutline);

  window.addEventListener('mousemove', (e) => {
    const posX = e.clientX;
    const posY = e.clientY;

    // Dot follows instantly
    cursorDot.style.left = `${posX}px`;
    cursorDot.style.top = `${posY}px`;

    // Outline follows with delay
    cursorOutline.animate({
      left: `${posX}px`,
      top: `${posY}px`
    }, { duration: 500, fill: "forwards" });
  });
}


document.addEventListener('DOMContentLoaded', () => {
  // 1. Set Date in Hero
  const dateElement = document.getElementById('daily-date');
  if (dateElement) {
    dateElement.textContent = getFormattedDate();
  }

  // 2. Render Grids
  renderGrid(recommendations.movies, 'movies-grid', 'Cinema');
  renderGrid(recommendations.music, 'music-grid', 'Music');
  renderGrid(recommendations.books, 'books-grid', 'Literature');

  initCursor();

  // Navigation Scroll
  document.querySelectorAll('.dock-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.querySelector(link.getAttribute('href'));
      target.scrollIntoView({ behavior: 'smooth' });

      // Update active state
      document.querySelectorAll('.dock-link').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
    });
  });

  // Delay animations slightly to ensure DOM is ready
  setTimeout(initAnimations, 100);
});
