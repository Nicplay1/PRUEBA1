// detalle_reserva_pagos.js - Código corregido

// =======================
// Variables Globales
// =======================
let sidebar, overlay, toggleBtn, mainContent;

// =======================
// Inicialización cuando el DOM esté listo
// =======================
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar variables
    sidebar = document.getElementById('sidebar');
    overlay = document.getElementById('sidebarOverlay');
    toggleBtn = document.getElementById('toggleSidebar');
    mainContent = document.getElementById('mainContent');

    // Inicializar funcionalidades
    initSidebar();
    initFormEnhancements();
    initAutoHideAlerts();
});

// =======================
// Sidebar Functionality
// =======================
function initSidebar() {
    if (!toggleBtn || !sidebar || !overlay) {
        console.warn('Elementos del sidebar no encontrados');
        return;
    }

    function toggleSidebar() {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    }

    toggleBtn.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);

    // Cerrar sidebar con tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            toggleSidebar();
        }
    });

    // Manejo responsive automático
    function handleResize() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    }
    window.addEventListener('resize', handleResize);
}

// =======================
// Form Enhancements
// =======================
function initFormEnhancements() {
    const formInputs = document.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        if (!input.classList.contains('form-check-input')) {
            input.classList.add('form-control-modern');
        }
    });
}

// =======================
// Auto-hide Alerts
// =======================
function initAutoHideAlerts() {
    setTimeout(() => {
        document.querySelectorAll('.alert-modern').forEach(el => {
            el.classList.remove('show');
            setTimeout(() => el.remove(), 300);
        });
    }, 5000);
}

// =======================
// Actualizar estado de pago
// =======================
function actualizarEstadoPago(checkbox, pagoId) {
    const formData = new FormData();
    formData.append('pago_id', pagoId);
    formData.append('estado', checkbox.checked ? 'True' : 'False');

    fetch(window.location.href, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del servidor');
        }
        return response;
    })
    .then(() => {
        const badge = document.getElementById('badge-' + pagoId);
        if (badge) {
            badge.textContent = checkbox.checked ? 'Aprobado' : 'Pendiente';
            badge.className = checkbox.checked ? 'badge badge-success' : 'badge badge-warning';
        }
    })
    .catch(error => {
        console.error('Error al actualizar estado de pago:', error);
        // Revertir el cambio en caso de error
        checkbox.checked = !checkbox.checked;
        alert('Error al actualizar el estado del pago');
    });
}

// =======================
// Función para obtener CSRF de cookies
// =======================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// =======================
// Utility Functions
// =======================
function showAlert(message, type = 'success') {
    const alertContainer = document.querySelector('.alerts-container') || createAlertContainer();
    const alert = document.createElement('div');
    alert.className = `alert-modern alert-${type} fade show`;
    alert.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : 'exclamation'}-circle"></i>
        <div>${message}</div>
    `;
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.className = 'alerts-container';
    document.body.prepend(container);
    return container;
}