document.addEventListener("DOMContentLoaded", function () {
    const torreSelect = document.getElementById("id_torre");
    const apartamentoSelect = document.getElementById("id_apartamento");
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    // --- Auto-cierre de alertas ---
    setTimeout(() => {
        document.querySelectorAll('.alert-modern').forEach(el => {
            el.classList.remove('show');
            setTimeout(() => el.remove(), 300);
        });
    }, 4000);

    // --- Filtrado de apartamentos (si se necesita) ---
    if (torreSelect && apartamentoSelect) {
        torreSelect.addEventListener("change", function () {
            for (let option of apartamentoSelect.options) {
                option.style.display = "block";
            }
        });
    }

    // --- Detectar si es móvil ---
    if (isMobile) {
        if (torreSelect) replaceSelectWithModal(torreSelect);
        if (apartamentoSelect) replaceSelectWithModal(apartamentoSelect);
    } else {
        fixSelectDropdowns();
    }

    // --- Funciones internas ---
    function replaceSelectWithModal(selectElement) {
        const originalSelect = selectElement;
        originalSelect.style.display = 'none';
        
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'form-control';
        button.style.textAlign = 'left';
        button.innerHTML = originalSelect.options[originalSelect.selectedIndex]?.text || 'Seleccionar...';
        
        originalSelect.parentNode.insertBefore(button, originalSelect);
        
        button.addEventListener('click', function() {
            openMobileSelect(originalSelect, button);
        });
    }

    function openMobileSelect(selectElement, button) {
        const modal = document.getElementById('mobileSelectModal');
        const title = document.getElementById('mobileSelectTitle');
        const optionsContainer = document.getElementById('mobileSelectOptions');
        
        title.textContent = `Seleccionar ${selectElement.name === 'torre' ? 'Torre' : 'Apartamento'}`;
        optionsContainer.innerHTML = '';
        
        for (let i = 0; i < selectElement.options.length; i++) {
            const option = selectElement.options[i];
            const optionElement = document.createElement('div');
            optionElement.className = 'mobile-select-option';
            optionElement.textContent = option.text;
            optionElement.addEventListener('click', function() {
                selectElement.selectedIndex = i;
                button.textContent = option.text;
                closeMobileSelect();
            });
            optionsContainer.appendChild(optionElement);
        }
        
        modal.style.display = 'flex';
    }

    window.closeMobileSelect = function () {
        const modal = document.getElementById('mobileSelectModal');
        modal.style.display = 'none';
    }

    function fixSelectDropdowns() {
        // Asegura que los select siempre se abran hacia abajo
        const selects = document.querySelectorAll('select.form-control');
        selects.forEach(select => {
            select.style.position = 'relative';
            select.style.zIndex = '10';
            select.style.transform = 'translate3d(0,0,0)';
            select.style.webkitTransform = 'translate3d(0,0,0)';
            select.style.overflow = 'visible';

            const container = select.closest('.main-container');
            if (container) {
                container.style.overflow = 'visible';
            }
        });

        const style = document.createElement('style');
        style.innerHTML = `
            select.form-control {
                overflow: visible !important;
            }
            .main-container, body {
                overflow: visible !important;
            }
        `;
        document.head.appendChild(style);
    }
});
