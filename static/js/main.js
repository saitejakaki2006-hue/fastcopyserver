// Color mapping for different services
const serviceThemes = {
    'Printing': '#2563eb',
    'Spiral Binding': '#9333ea',
    'Soft Binding': '#db2777',
    'Custom Printing': '#059669',
    'Thesis Binding': '#d97706',
    'Photo Frames': '#dc2626'
};

// Function to handle Service Switching
function selectService(name, id) {
    const titleElement = document.getElementById('current-service-title');
    const headerElement = document.getElementById('form-header');
    
    if (titleElement) titleElement.innerText = name;
    if (headerElement) headerElement.style.backgroundColor = serviceThemes[name] || '#2563eb';
    
    // Tab Highlighting Logic
    document.querySelectorAll('.service-tab').forEach(tab => {
        tab.classList.remove('active-service-tab');
    });
    
    const activeBtn = document.getElementById('btn-' + id);
    if (activeBtn) activeBtn.classList.add('active-service-tab');
    
    calculatePrice();
}

// Function to calculate dynamic pricing
function calculatePrice() {
    const typeElement = document.getElementById('ptype');
    const copiesElement = document.getElementById('pcopies');
    const priceDisplay = document.getElementById('final-price');

    if (typeElement && copiesElement && priceDisplay) {
        const rate = parseFloat(typeElement.value);
        const copies = parseInt(copiesElement.value) || 1;
        priceDisplay.innerText = (rate * copies).toFixed(0);
    }
}

// Initialize default service on load
document.addEventListener('DOMContentLoaded', () => {
    const firstTab = document.querySelector('.service-tab');
    if (firstTab) firstTab.click();
    
    // Initialize AOS
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 1000, once: true });
    }
});
// Configuration for Service Themes
const serviceConfig = {
    'Printing': { color: '#2563eb', rate: 2 },
    'Spiral Binding': { color: '#9333ea', rate: 45 },
    'Soft Binding': { color: '#db2777', rate: 60 },
    'Custom Printing': { color: '#059669', rate: 15 },
    'Thesis Binding': { color: '#d97706', rate: 150 },
    'Photo Frames': { color: '#dc2626', rate: 200 }
};

function selectService(serviceName, buttonId) {
    const config = serviceConfig[serviceName] || serviceConfig['Printing'];

    // 1. Update Form Header & Title
    document.getElementById('display-service-name').innerText = serviceName;
    document.getElementById('form-header-bg').style.backgroundColor = config.color;
    document.getElementById('price-label').style.color = config.color;

    // 2. Update Tabs UI
    document.querySelectorAll('.service-tab').forEach(tab => {
        tab.classList.remove('active-tab');
    });
    document.getElementById('btn-' + buttonId).classList.add('active-tab');

    // 3. Reset and Recalculate Price
    calculatePrice(config.rate);
}

function calculatePrice(baseRate) {
    const typeMultiplier = document.getElementById('printType').value === 'color' ? 5 : 1; // Color is 5x more
    const sideMultiplier = document.getElementById('sideType').value; // Multipliers like 1, 2, 0.5 etc.
    const copies = parseInt(document.getElementById('copiesCount').value) || 1;

    // Logic: Base Rate * Type * Side * Copies
    // For simplicity: (Base Rate * Type) * Copies
    let total = (baseRate * typeMultiplier) * copies;
    
    document.getElementById('total-amount').innerText = total.toLocaleString('en-IN');
}

// Initial Setup
document.addEventListener('DOMContentLoaded', () => {
    // Trigger the first service by default
    const firstTab = document.querySelector('.service-tab');
    if (firstTab) firstTab.click();
});