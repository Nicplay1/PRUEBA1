setTimeout(() => {
            document.querySelectorAll('.alert-modern').forEach(el => {
                el.classList.remove('show');
                setTimeout(() => el.remove(), 300);
            });
        }, 4000);


    // Script para el sidebar y modales 
// =========================
        // Toggle Sidebar
        // =========================
        const toggleBtn = document.getElementById('toggleSidebar');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        const modalOverlay = document.getElementById('overlay');

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

        // =========================
        // Control del overlay para modales
        // =========================
        function showModalOverlay() {
            modalOverlay.style.display = 'block';
        }

        function hideModalOverlay() {
            modalOverlay.style.display = 'none';
        }

        function closeAllModals() {
            // Cerrar todos los modales de Bootstrap
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
            hideModalOverlay();
        }

        // Configurar eventos para todos los modales
        document.addEventListener('DOMContentLoaded', function() {
            const modals = document.querySelectorAll('.modal');
            
            modals.forEach(modal => {
                modal.addEventListener('show.bs.modal', function() {
                    showModalOverlay();
                });
                
                modal.addEventListener('hidden.bs.modal', function() {
                    hideModalOverlay();
                });
            });

            // Cerrar modales con tecla Escape
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    closeAllModals();
                }
            });
        });