// Main JS for POS functions

// Cart management for Sales
let cart = [];

function addToCart(productId, qty = 1) {
  // AJAX to add
  console.log(`Added ${qty} of ${productId} to cart`);
}

function renderProducts(products) {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  const safeArray = Array.isArray(products) ? products : [];

  grid.innerHTML = safeArray.length
    ? safeArray
        .map((p) => {
          const imgHtml = p.image_url
            ? `<img src="${p.image_url}" class="card-img-top" alt="${p.name}">`
            : '';

          return `
            <div class="col-md-4 mb-4">
              <div class="card">
                ${imgHtml}
                <div class="card-body">
                  <h5 class="card-title">${p.name || ''}</h5>
                  <p class="card-text">${(p.description || '').slice(0, 140)}</p>
                  <p class="fw-bold">$${p.price ?? ''}</p>
                  <button class="btn btn-success" onclick="addToCart(${p.id})">Add to Cart</button>
                </div>
              </div>
            </div>
          `;
        })
        .join('')
    : `<p>No products available.</p>`;
}

async function loadProductsFromApi() {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  try {
    const res = await fetch('/api/products/', { method: 'GET' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    // With DRF pagination disabled, this should already be an array.
    renderProducts(data);
  } catch (err) {
    console.warn('Failed to load products from API; keeping server-rendered content.', err);
  }
}

// Dashboard charts later with Chart.js

document.addEventListener('DOMContentLoaded', () => {
  loadProductsFromApi();
});

