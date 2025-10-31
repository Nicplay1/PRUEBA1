// Manejo del sidebar
const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

function toggleSidebar() {
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

if (toggleBtn && overlay) {
    toggleBtn.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);
}

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

// Alertas automáticas (desaparecen después de 4 segundos)
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert-modern');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            });
        }, 4000);
    }
});
