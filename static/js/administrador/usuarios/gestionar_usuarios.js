document.addEventListener("DOMContentLoaded", function () {
    // Obtener URLs desde atributos data
    const gestionarUsuariosUrl = document.body.dataset.gestionarUsuariosUrl;
    const searchInput = document.querySelector(".search-input");
    const resultadosDiv = document.getElementById("resultados-usuarios");

    // Modal elementos
    const confirmationModal = document.getElementById('confirmationModal');
    const userNameModal = document.getElementById('userNameModal');
    const roleNameModal = document.getElementById('roleNameModal');
    const cancelChangeBtn = document.getElementById('cancelChange');
    const confirmChangeBtn = document.getElementById('confirmChange');
    const loadingIndicator = document.getElementById('loadingIndicator');
    let currentForm = null;

    // CSRF Token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Mostrar modal al hacer clic en "Cambiar"
    function bindRoleForms() {
        document.querySelectorAll(".role-form").forEach(form => {
            const changeBtn = form.querySelector(".change-role-btn");
            changeBtn.addEventListener("click", function () {
                const userName = form.getAttribute('data-user-name');
                const roleSelect = form.querySelector('select[name="id_rol"]');
                const roleName = roleSelect.options[roleSelect.selectedIndex].textContent;

                userNameModal.textContent = userName;
                roleNameModal.textContent = roleName;

                currentForm = form;
                confirmationModal.classList.add('active');
            });
        });
    }

    // Confirmar cambio de rol con AJAX
    confirmChangeBtn.addEventListener("click", function () {
        if (!currentForm) return;

        const formData = new FormData(currentForm);
        loadingIndicator.classList.add('active');

        fetch(gestionarUsuariosUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrftoken
            }
        })
        .then(response => response.json())
        .then(data => {
            resultadosDiv.innerHTML = data.html;
            confirmationModal.classList.remove('active');
            loadingIndicator.classList.remove('active');
            bindRoleForms();

            // Mostrar notificación
            const notificaciones = document.getElementById("notificaciones");
            if (notificaciones) {
                const div = document.createElement("div");
                div.className = `alert-modern alert-${data.status}`;
                div.innerHTML = `
                    <i class="fas ${data.status === 'success' ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                    ${data.mensaje}
                `;
                notificaciones.appendChild(div);

                setTimeout(() => {
                    div.classList.remove('show');
                    setTimeout(() => div.remove(), 300);
                }, 4000);
            }
        })
        .catch(() => {
            loadingIndicator.classList.remove('active');
            alert("Error al cambiar el rol.");
        });

        currentForm = null;
    });

    // Cancelar modal
    cancelChangeBtn.addEventListener("click", function () {
        confirmationModal.classList.remove('active');
        currentForm = null;
    });

    // Buscar mientras escribe
    searchInput.addEventListener("keyup", function () {
        const query = searchInput.value;
        fetch(`${gestionarUsuariosUrl}?q=${encodeURIComponent(query)}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(response => response.json())
        .then(data => {
            resultadosDiv.innerHTML = data.html;
            bindRoleForms();
        });
    });

    // Sidebar
    const toggleBtn = document.getElementById('toggleSidebar');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    function toggleSidebar() {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    }

    toggleBtn.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            toggleSidebar();
        }
    });

    function handleResize() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    }

    window.addEventListener('resize', handleResize);

    // Inicialización
    bindRoleForms();
});
