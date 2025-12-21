/**
 * FAST COPY - MASTER JAVASCRIPT ENGINE
 * Version: 8.5 (Final Integrated Build)
 * Purpose: Handles PDF analysis, Dynamic Pricing, Profile Sync, and UI Animations.
 */

let globalPageCount = 0; // Tracks document pages for real-time pricing

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize AOS (Animate On Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 1000,
            once: true,
            offset: 50,
            easing: 'ease-out-back'
        });
    }

    // 2. Global Event Listeners for Pricing Hub
    const pricingInputs = document.querySelectorAll('#pType, #sType, #copies');
    pricingInputs.forEach(input => {
        input.addEventListener('change', () => {
            updateLabels();
            calculatePrice();
        });
        input.addEventListener('input', calculatePrice);
    });
});

/**
 * 1. PRICING CALCULATION ENGINE
 * Formula: Pages * Base Price * Side Multiplier * Copies
 */
function calculatePrice() {
    const pPrice = parseFloat(document.getElementById('pType')?.value) || 0;
    const sMultiplier = parseFloat(document.getElementById('sType')?.value) || 1;
    const copies = parseInt(document.getElementById('copies')?.value) || 1;

    let total = Math.round(globalPageCount * pPrice * sMultiplier * copies);

    const priceDisplay = document.getElementById('price-display');
    const hiddenPriceInput = document.getElementById('total-price-hidden');

    if (priceDisplay) priceDisplay.innerText = total;
    if (hiddenPriceInput) hiddenPriceInput.value = total;

    updateLabels();
}

/**
 * 2. PDF ANALYSIS (AJAX)
 * Extracts page count from server and triggers pricing update.
 */
function handleFileUpload(event, apiUrl, csrfToken) {
    const file = event.target.files[0];
    const fileStatus = document.getElementById('file-status-text');
    const pageBadge = document.getElementById('page-count-badge');

    if (!file) return;

    fileStatus.innerHTML = `<i class="fas fa-spinner fa-spin text-blue-500 mr-2"></i> Analyzing ${file.name}...`;

    const formData = new FormData();
    formData.append('document', file);
    formData.append('csrfmiddlewaretoken', csrfToken);

    fetch(apiUrl, { method: 'POST', body: formData })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            globalPageCount = data.pages; 
            fileStatus.innerHTML = `<i class="fas fa-check-circle text-green-500 mr-2"></i> Uploaded: ${file.name}`;
            if (pageBadge) pageBadge.innerText = `Pages: ${globalPageCount}`;
            calculatePrice(); 
            showToast("Document Analyzed Successfully", "success");
        } else {
            fileStatus.innerHTML = `<span class="text-red-500">Analysis Failed</span>`;
            showToast(data.message || "Error reading PDF", "error");
        }
    })
    .catch(() => showToast("Server Connection Error", "error"));
}

/**
 * 3. PROFILE UPDATE ENGINE (AJAX)
 * Syncs profile changes without refreshing the page.
 */
function handleProfileUpdate(event, apiUrl) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerText;

    // Loading State
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Syncing Hub...';
    submitBtn.disabled = true;

    fetch(apiUrl, {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': formData.get('csrfmiddlewaretoken') }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI elements instantly
            document.querySelectorAll('.user-name-display').forEach(el => {
                el.innerText = formData.get('name');
            });
            
            const mobileDisp = document.getElementById('sidebar-mobile-display');
            const addrDisp = document.getElementById('sidebar-address-display');
            
            if (mobileDisp) mobileDisp.innerText = '+91 ' + formData.get('mobile');
            if (addrDisp) addrDisp.innerText = formData.get('address');

            showToast("Profile Updated Successfully", "success");
            
            // Hide Modal
            const modalEl = document.getElementById('editProfileModal');
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) modalInstance.hide();
        } else {
            showToast(data.message || "Update Failed", "error");
        }
    })
    .catch(() => showToast("Network Sync Error", "error"))
    .finally(() => {
        submitBtn.innerText = originalBtnText;
        submitBtn.disabled = false;
    });
}

/**
 * 4. UI UTILITIES (Toasts & Labels)
 */
function updateLabels() {
    const pSelect = document.getElementById('pType');
    const sSelect = document.getElementById('sType');
    if (pSelect && sSelect) {
        const pLabel = document.getElementById('p-label-hidden');
        const sLabel = document.getElementById('s-label-hidden');
        if (pLabel) pLabel.value = pSelect.options[pSelect.selectedIndex].text;
        if (sLabel) sLabel.value = sSelect.options[sSelect.selectedIndex].text;
    }
}

function showToast(message, type) {
    const existing = document.querySelector('.custom-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    const color = type === 'success' ? 'bg-green-600' : 'bg-red-600';
    
    toast.className = `custom-toast fixed bottom-10 right-10 ${color} text-white px-8 py-4 rounded-full shadow-2xl z-[2000] font-black uppercase tracking-widest text-[10px] animate-bounce`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-triangle-exclamation'} mr-2"></i> ${message}`;
    
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

function updateCartBadge(count) {
    const badge = document.getElementById('cart-count-badge');
    if (badge) {
        badge.innerText = count;
        badge.style.transform = 'scale(1.8)';
        setTimeout(() => badge.style.transform = 'scale(1)', 300);
    }
}