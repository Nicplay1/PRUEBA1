// =========================
// ALERTAS AUTOMÁTICAS
// =========================
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        document.querySelectorAll(".alert-modern").forEach(el => {
            el.classList.remove("show");
            setTimeout(() => el.remove(), 300);
        });
    }, 4000);
});

// =========================
// TOGGLE SIDEBAR
// =========================
const toggleBtn = document.getElementById("toggleSidebar");
const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("sidebarOverlay");
const modalOverlay = document.getElementById("overlay");

function toggleSidebar() {
    sidebar.classList.toggle("active");
    overlay.classList.toggle("active");
}

if (toggleBtn && overlay) {
    toggleBtn.addEventListener("click", toggleSidebar);
    overlay.addEventListener("click", toggleSidebar);
}

// Cerrar sidebar con tecla Escape
document.addEventListener("keydown", e => {
    if (e.key === "Escape" && sidebar.classList.contains("active")) {
        toggleSidebar();
    }
});

// Ajuste automático en pantallas grandes
window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
        sidebar.classList.remove("active");
        overlay.classList.remove("active");
    }
});

// =========================
// CONTROL DEL OVERLAY DE MODALES
// =========================
function showModalOverlay() {
    modalOverlay.style.display = "block";
}

function hideModalOverlay() {
    modalOverlay.style.display = "none";
}

function closeAllModals() {
    const modals = document.querySelectorAll(".modal");
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) modalInstance.hide();
    });
    hideModalOverlay();
}

// =========================
// CONFIGURAR EVENTOS DE MODALES
// =========================
document.addEventListener("DOMContentLoaded", () => {
    const modals = document.querySelectorAll(".modal");
    
    modals.forEach(modal => {
        modal.addEventListener("show.bs.modal", showModalOverlay);
        modal.addEventListener("hidden.bs.modal", hideModalOverlay);
    });

    // Cerrar modales con tecla Escape
    document.addEventListener("keydown", e => {
        if (e.key === "Escape") closeAllModals();
    });
});
